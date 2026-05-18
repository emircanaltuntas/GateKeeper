import simpy
import random
import statistics


class AgGecidi:
    def __init__(self, env, kapasite, kuyruk_siniri, suspicious_threshold, normal_threshold):
        self.env = env
        self.sunucu = simpy.PriorityResource(env, capacity=kapasite)
        self.kuyruk_siniri = kuyruk_siniri
        self.suspicious_threshold = suspicious_threshold
        self.normal_threshold = normal_threshold

        self.islenen = {"admin": 0, "normal": 0, "suspicious": 0}
        self.drop_edilen = {"admin": 0, "normal": 0, "suspicious": 0}
        self.bekleme_sureleri = {"admin": [], "normal": [], "suspicious": []}
        self.kuyruk_gecmisi = []
        self.paket_olaylari = []

    def kuyruk_uzunlugu(self):
        return len(self.sunucu.queue) + self.sunucu.count

    def drop_karari(self, paket_turu):
        kuyruk_len = self.kuyruk_uzunlugu()
        if paket_turu == "admin":
            return False
        elif paket_turu == "suspicious" and kuyruk_len >= self.suspicious_threshold:
            return True
        elif paket_turu == "normal" and kuyruk_len >= self.normal_threshold:
            return True
        return False


class PaketUretici:
    def __init__(self, env, ag_gecidi, paket_turu, oncelik, ortalama_aralik, islem_suresi):
        self.env = env
        self.ag_gecidi = ag_gecidi
        self.paket_turu = paket_turu
        self.oncelik = oncelik
        self.ortalama_aralik = ortalama_aralik
        self.islem_suresi = islem_suresi

    def uret(self):
        paket_id = 0
        while True:
            aralik = random.expovariate(1.0 / self.ortalama_aralik)
            yield self.env.timeout(aralik)
            paket_id += 1
            self.env.process(self.paket_isle(paket_id))

    def paket_isle(self, paket_id):
        varis_zamani = self.env.now

        if self.ag_gecidi.drop_karari(self.paket_turu):
            self.ag_gecidi.drop_edilen[self.paket_turu] += 1
            self.ag_gecidi.paket_olaylari.append({
                "zaman": self.env.now,
                "tur": self.paket_turu,
                "durum": "drop",
                "paket_id": paket_id
            })
            return

        req = self.ag_gecidi.sunucu.request(priority=self.oncelik)
        yield req

        bekleme = self.env.now - varis_zamani
        self.ag_gecidi.bekleme_sureleri[self.paket_turu].append(bekleme)

        islem_suresi = random.expovariate(1.0 / self.islem_suresi)
        yield self.env.timeout(islem_suresi)

        self.ag_gecidi.sunucu.release(req)
        self.ag_gecidi.islenen[self.paket_turu] += 1
        self.ag_gecidi.paket_olaylari.append({
            "zaman": self.env.now,
            "tur": self.paket_turu,
            "durum": "islendi",
            "paket_id": paket_id
        })


def kuyruk_izle(env, ag_gecidi, aralik=1.0):
    while True:
        ag_gecidi.kuyruk_gecmisi.append({
            "zaman": env.now,
            "doluluk": ag_gecidi.kuyruk_uzunlugu()
        })
        yield env.timeout(aralik)


def simulasyonu_calistir(seed, kapasite, kuyruk_siniri, suspicious_threshold,
                         normal_threshold, sim_suresi, admin_aralik,
                         normal_aralik, suspicious_aralik, islem_suresi=1.5):
    random.seed(seed)
    env = simpy.Environment()

    ag_gecidi = AgGecidi(env, kapasite, kuyruk_siniri, suspicious_threshold, normal_threshold)

    ureticiler = [
        PaketUretici(env, ag_gecidi, "admin", 0, admin_aralik, islem_suresi),
        PaketUretici(env, ag_gecidi, "normal", 1, normal_aralik, islem_suresi),
        PaketUretici(env, ag_gecidi, "suspicious", 2, suspicious_aralik, islem_suresi),
    ]

    for u in ureticiler:
        env.process(u.uret())

    env.process(kuyruk_izle(env, ag_gecidi))

    env.run(until=sim_suresi)

    ort_bekleme = {}
    for tur, sureler in ag_gecidi.bekleme_sureleri.items():
        ort_bekleme[tur] = statistics.mean(sureler) if sureler else 0.0

    return {
        "islenen": ag_gecidi.islenen,
        "drop_edilen": ag_gecidi.drop_edilen,
        "ort_bekleme": ort_bekleme,
        "kuyruk_gecmisi": ag_gecidi.kuyruk_gecmisi,
        "paket_olaylari": ag_gecidi.paket_olaylari,
    }
