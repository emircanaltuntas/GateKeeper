import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from simulation import simulasyonu_calistir

st.set_page_config(page_title="GateKeeper", page_icon="🛡️", layout="wide")

st.title("GateKeeper — Ağ Geçidi Trafik ve Güvenlik Simülasyonu")
st.markdown("SimPy tabanlı öncelikli kuyruk yönetimi ve katmanlı drop politikası simülasyonu")

st.sidebar.header("Simülasyon Parametreleri")

seed = st.sidebar.number_input("Rastgele Seed", min_value=0, max_value=9999, value=42)
sim_suresi = st.sidebar.slider("Simülasyon Süresi (birim zaman)", 50, 500, 200)
kapasite = st.sidebar.slider("Sunucu Kapasitesi", 1, 10, 3)
kuyruk_siniri = st.sidebar.slider("Kuyruk Sınırı (Şüpheli Drop Eşiği)", 5, 30, 10)
normal_threshold = st.sidebar.slider("Normal Paket Drop Eşiği", 5, 40, 13)

st.sidebar.subheader("Paket Geliş Aralıkları")
admin_aralik = st.sidebar.slider("Admin Ort. Geliş Aralığı", 1.0, 20.0, 8.0, 0.5)
normal_aralik = st.sidebar.slider("Normal Ort. Geliş Aralığı", 0.5, 10.0, 2.0, 0.5)
suspicious_aralik = st.sidebar.slider("Şüpheli Ort. Geliş Aralığı", 0.5, 10.0, 1.2, 0.1)

islem_suresi = st.sidebar.slider("Ort. İşlem Süresi", 0.5, 5.0, 1.5, 0.5)

if st.sidebar.button("Simülasyonu Başlat", type="primary", use_container_width=True):
    with st.spinner("Simülasyon çalışıyor..."):
        sonuc = simulasyonu_calistir(
            seed=seed,
            kapasite=kapasite,
            kuyruk_siniri=kuyruk_siniri,
            suspicious_threshold=kuyruk_siniri,
            normal_threshold=normal_threshold,
            sim_suresi=sim_suresi,
            admin_aralik=admin_aralik,
            normal_aralik=normal_aralik,
            suspicious_aralik=suspicious_aralik,
            islem_suresi=islem_suresi,
        )
    st.session_state["sonuc"] = sonuc

if "sonuc" in st.session_state:
    sonuc = st.session_state["sonuc"]

    st.header("Özet İstatistikler")
    col1, col2, col3 = st.columns(3)

    toplam_islenen = sum(sonuc["islenen"].values())
    toplam_drop = sum(sonuc["drop_edilen"].values())

    with col1:
        st.metric("Toplam İşlenen Paket", toplam_islenen)
    with col2:
        st.metric("Toplam Drop Edilen Paket", toplam_drop)
    with col3:
        oran = (toplam_drop / (toplam_islenen + toplam_drop) * 100) if (toplam_islenen + toplam_drop) > 0 else 0
        st.metric("Genel Drop Oranı", f"%{oran:.1f}")

    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("Admin İşlenen / Drop", f"{sonuc['islenen']['admin']} / {sonuc['drop_edilen']['admin']}")
    with col5:
        st.metric("Normal İşlenen / Drop", f"{sonuc['islenen']['normal']} / {sonuc['drop_edilen']['normal']}")
    with col6:
        st.metric("Şüpheli İşlenen / Drop", f"{sonuc['islenen']['suspicious']} / {sonuc['drop_edilen']['suspicious']}")

    st.header("Kuyruk Doluluk Grafiği")
    df_kuyruk = pd.DataFrame(sonuc["kuyruk_gecmisi"])
    fig_kuyruk = go.Figure()
    fig_kuyruk.add_trace(go.Scatter(
        x=df_kuyruk["zaman"], y=df_kuyruk["doluluk"],
        mode="lines", name="Kuyruk Doluluk", line=dict(color="#1f77b4")
    ))
    fig_kuyruk.add_hline(y=kuyruk_siniri, line_dash="dash", line_color="orange",
                         annotation_text=f"Şüpheli Drop Eşiği ({kuyruk_siniri})")
    fig_kuyruk.add_hline(y=normal_threshold, line_dash="dash", line_color="red",
                         annotation_text=f"Normal Drop Eşiği ({normal_threshold})")
    fig_kuyruk.update_layout(
        xaxis_title="Zaman", yaxis_title="Kuyruk Doluluk",
        height=400, margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig_kuyruk, use_container_width=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.header("Drop Oranı Dağılımı")
        drop_values = sonuc["drop_edilen"]
        if toplam_drop > 0:
            fig_pasta = go.Figure(data=[go.Pie(
                labels=["Admin", "Normal", "Şüpheli"],
                values=[drop_values["admin"], drop_values["normal"], drop_values["suspicious"]],
                marker=dict(colors=["#2ecc71", "#3498db", "#e74c3c"]),
                hole=0.3
            )])
            fig_pasta.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_pasta, use_container_width=True)
        else:
            st.info("Hiç paket drop edilmedi.")

    with col_right:
        st.header("Ortalama Bekleme Süreleri")
        bekleme_df = pd.DataFrame({
            "Paket Türü": ["Admin", "Normal", "Şüpheli"],
            "Ort. Bekleme": [
                sonuc["ort_bekleme"]["admin"],
                sonuc["ort_bekleme"]["normal"],
                sonuc["ort_bekleme"]["suspicious"],
            ]
        })
        fig_bar = px.bar(bekleme_df, x="Paket Türü", y="Ort. Bekleme",
                         color="Paket Türü",
                         color_discrete_map={"Admin": "#2ecc71", "Normal": "#3498db", "Şüpheli": "#e74c3c"})
        fig_bar.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20), showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.header("Zaman Dilimi Isı Haritası")
    df_olaylar = pd.DataFrame(sonuc["paket_olaylari"])
    if not df_olaylar.empty:
        num_bins = 20
        df_olaylar["zaman_dilimi"] = pd.cut(df_olaylar["zaman"], bins=num_bins, labels=False)
        heatmap_data = df_olaylar.groupby(["zaman_dilimi", "tur"]).size().unstack(fill_value=0)
        for col in ["admin", "normal", "suspicious"]:
            if col not in heatmap_data.columns:
                heatmap_data[col] = 0
        heatmap_data = heatmap_data[["admin", "normal", "suspicious"]]

        fig_heat = go.Figure(data=go.Heatmap(
            z=heatmap_data.values.T,
            x=[f"Dilim {i+1}" for i in range(len(heatmap_data))],
            y=["Admin", "Normal", "Şüpheli"],
            colorscale="YlOrRd"
        ))
        fig_heat.update_layout(
            xaxis_title="Zaman Dilimi", yaxis_title="Paket Türü",
            height=300, margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    st.header("Paket Olay Akışı")
    if not df_olaylar.empty:
        fig_scatter = go.Figure()
        renk_map = {"admin": "#2ecc71", "normal": "#3498db", "suspicious": "#e74c3c"}
        sembol_map = {"islendi": "circle", "drop": "x"}
        for tur in ["admin", "normal", "suspicious"]:
            for durum in ["islendi", "drop"]:
                filtre = df_olaylar[(df_olaylar["tur"] == tur) & (df_olaylar["durum"] == durum)]
                if not filtre.empty:
                    fig_scatter.add_trace(go.Scatter(
                        x=filtre["zaman"], y=filtre["tur"],
                        mode="markers",
                        marker=dict(color=renk_map[tur],
                                    symbol=sembol_map[durum],
                                    size=6 if durum == "islendi" else 8),
                        name=f"{tur.capitalize()} ({durum})"
                    ))
        fig_scatter.update_layout(
            xaxis_title="Zaman", yaxis_title="Paket Türü",
            height=300, margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

else:
    st.info("Soldaki panelden parametreleri ayarlayıp 'Simülasyonu Başlat' butonuna basın.")
