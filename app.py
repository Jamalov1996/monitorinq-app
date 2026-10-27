import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Özünüməşğulluq Monitorinq Bazası", layout="centered")

if "staff_db" not in st.session_state:
    st.session_state.staff_db = {
        "123456": {"name": "Camalov Rəfiq Əli oğlu", "pass": "qabil123"},
        "654321": {"name": "Həsənov Anar Rasim oğlu", "pass": "anar456"}
    }

if "office_list" not in st.session_state:
    st.session_state.office_list = pd.DataFrame(columns=[
        "FIN", "SAA", "Zarf", "Rayon_Ofis", "Monitorinq_Novu"
    ])

if "results_db" not in st.session_state:
    st.session_state.results_db = pd.DataFrame()

is_emp_logged = "logged_emp_id" in st.session_state
is_admin_logged = st.session_state.get("is_admin", False)

# Əgər heç kim daxil olmayıbsa, birbaşa əsas ekranda Giriş formasını göstər
if not is_emp_logged and not is_admin_logged:
    st.title("🔐 Sistemə Giriş")
    role = st.radio("Rolunuzu seçin:", ["Monitorinq Əməkdaşı", "Ofis Əməkdaşı (Admin)"])

    if role == "Ofis Əməkdaşı (Admin)":
        admin_login = st.text_input("Login")
        admin_pass = st.text_input("Şifrə", type="password")
        
        if st.button("Admin Girişi"):
            if admin_login == "admin" and admin_pass == "admin123":
                st.session_state.is_admin = True
                st.success("Admin kimi daxil oldunuz!")
                st.rerun()
            else:
                st.error("Yanlış login və ya şifrə!")

    elif role == "Monitorinq Əməkdaşı":
        emp_id = st.text_input("Şəxsi İD")
        emp_pass = st.text_input("Şifrə", type="password")
        
        login_btn = st.button("Daxil ol")
        
        if login_btn:
            if emp_id in st.session_state.staff_db and st.session_state.staff_db[emp_id]["pass"] == emp_pass:
                st.session_state.logged_emp_id = emp_id
                st.session_state.logged_emp_name = st.session_state.staff_db[emp_id]["name"]
                st.success(f"Xoş gəldiniz, {st.session_state.logged_emp_name}!")
                st.rerun()
            else:
                st.error("İD və ya şifrə yanlışdır!")

elif is_admin_logged:
    st.title("📊 Ofis Paneli - Məlumatların İdarə Edilməsi")
    if st.button("🚪 Sistemdən çıxış"):
        st.session_state.is_admin = False
        st.rerun()
        
    uploaded_file = st.file_uploader("Həftəlik Excel siyahısını yüklə", type=["xlsx", "xls"])
    if uploaded_file is not None:
        st.session_state.office_list = pd.read_excel(uploaded_file)
        st.success("Siyahı bazaya uğurla əlavə olundu!")
        
    st.subheader("Mövcud Ofis Siyahısı:")
    st.dataframe(st.session_state.office_list)
    
    if not st.session_state.results_db.empty:
        st.subheader("Monitorinq Nəticələrinin Export Edilməsi")
        csv = st.session_state.results_db.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Nəticələri Excel/CSV olaraq yüklə",
            data=csv,
            file_name=f"monitorinq_hesabat_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
    else:
        st.info("Hələ ki daxil edilmiş monitorinq nəticəsi yoxdur.")

elif is_emp_logged:
    st.title("📝 Özünüməşğulluq Monitorinq Paneli")
    col_top1, col_top2 = st.columns([3, 1])
    with col_top1:
        st.write(f"İşləyən əməkdaş: **{st.session_state.logged_emp_name}**")
    with col_top2:
        if st.button("Çıxış"):
            del st.session_state.logged_emp_id
            del st.session_state.logged_emp_name
            st.rerun()
            
    fin_input = st.text_input("Vətəndaşın FİN-ini daxil edin (Axtarış üçün):").strip()
    
    if fin_input:
        df_office = st.session_state.office_list
        if not df_office.empty and "FIN" in df_office.columns:
            citizen = df_office[df_office["FIN"].astype(str) == fin_input]
        else:
            citizen = pd.DataFrame()
            
             # Excel-dən tapılan vətəndaşın məlumatlarını oxumaq
     if not citizen.empty:
         cit_row = citizen.iloc[0]
         val_saa = str(cit_row.get("SAA", ""))
         val_zarf = str(cit_row.get("Zarf", ""))
         val_rayon = str(cit_row.get("Rayon_Ofis", "Abşeron"))
         val_nov = str(cit_row.get("Monitorinq_Novu", "İlkin"))
     else:
         val_saa = "Tapılmadı (Excel-də bu FİN yoxdur)"
         val_zarf = "—"
         val_rayon = "Abşeron"
         val_nov = "İlkin"

     st.info("Vətəndaş məlumatları (Baxış rejimi):")
     col_g1, col_g2 = st.columns(2)
     with col_g1:
         st.text_input("Soyadı, Adı, Ata adı", value=val_saa, disabled=True)
         st.text_input("Müraciət Zərfi", value=val_zarf, disabled=True)
     with col_g2:
         office_rayon = st.selectbox("Rayon (Ofis)", ["Abşeron", "Sumqayıt", "Bakı", "Gəncə"], index=0, disabled=True)
         mon_novu = st.selectbox("Monitorinq Növü", ["İlkin", "Aralıq", "Yekun"])


        st.markdown("---")
        st.subheader("Monitorinq Nəticələrinin Daxil Edilməsi")
        
        status = st.radio("Statusu seçin:", ["Keçirildi", "Keçirilmədi"])
        mon_date = st.date_input("Monitorinq tarixi")
        
        if status == "Keçirildi":
            n1 = st.text_input("Nömrə 1 (Mütləq, məs: 0507796060)")
            n2 = st.text_input("Nömrə 2 (Mütləq)")
            n3 = st.text_input("Nömrə 3 (Arzuolunan)")
            mon_rayon = st.selectbox("Rayon (Monitorinq)", ["Abşeron", "Sumqayıt", "Bakı", "Gəncə"])
            
            if mon_novu == "İlkin" and mon_rayon != office_rayon:
                st.warning("⚠️ Diqqət! İlkin monitorinqdə Rayon (Monitorinq) ilə Rayon (Ofis) eyni olmalıdır!")
            elif mon_novu in ["Aralıq", "Yekun"] and mon_rayon != office_rayon:
                st.info("ℹ️ Qeyd: Monitorinq rayonu ofis rayonundan fərqlidir.")

            unvan = st.text_input("Ünvan (Mütləq)")
            
            if mon_novu in ["Aralıq", "Yekun"]:
                fealiyyet = st.selectbox("Fəaliyyət barədə:", [
                    "Aktivlər yerindədir, fəaliyyət göstərir", 
                    "Aktivlər yerindədir, fəaliyyət göstərmir", 
                    "Aktivlər satılıb və ya ziyan vurulub", 
                    "Aktivlər 3-cü şəxsdədir"
                ])
            else:
                fealiyyet = "—"
                
            qeyd = st.text_area("Qeyd (Arzuolunan)")
            
            if st.button("Yadda saxla"):
                if not n1 or not n2 or not unvan:
                    st.error("Zəhmət olmasa mütləq sahələri doldurun!")
                else:
                    save_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    new_row = {
                        "FIN": fin_input,
                        "Monitorinq_Novu": mon_novu,
                        "Status": status,
                        "Monitorinq_Tarixi": mon_date,
                        "Nomer_1": n1,
                        "Nomer_2": n2,
                        "Rayon_Monitorinq": mon_rayon,
                        "Unvan": unvan,
                        "Fealiyyet_Sebeb": fealiyyet,
                        "Qeyd": qeyd,
                        "Emekdas_SAA": st.session_state.logged_emp_name,
                        "Emekdas_ID": st.session_state.logged_emp_id,
                        "Sistem_Vaxti": save_time
                    }
                    df_new = pd.DataFrame([new_row])
                    st.session_state.results_db = pd.concat([st.session_state.results_db, df_new], ignore_index=True)
                    st.success(f"Məlumat uğurla yadda saxlanıldı! Vaxt: {save_time}")

        elif status == "Keçirilmədi":
            n1 = st.text_input("Nömrə 1 (Mütləq)")
            n2 = st.text_input("Nömrə 2 (Arzuolunan)")
            n3 = st.text_input("Nömrə 3 (Arzuolunan)")
            sebep = st.selectbox("Keçirilməmə səbəbi:", [
                "Əlaqə problemi", "Şərait yaratmadı", "İmtina etdi", 
                "Vəfat edib", "Ölkə xaricindədir", "Başqa rayonda yaşayır", "Digər"
            ])
            qeyd = st.text_area("Qeyd")
            
            if st.button("Yadda saxla"):
                if not n1:
                    st.error("Zəhmət olmasa Nömrə 1-i daxil edin!")
                else:
                    save_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    new_row = {
                        "FIN": fin_input,
                        "Monitorinq_Novu": mon_novu,
                        "Status": status,
                        "Monitorinq_Tarixi": mon_date,
                        "Nomer_1": n1,
                        "Nomer_2": n2,
                        "Rayon_Monitorinq": "—",
                        "Unvan": "—",
                        "Fealiyyet_Sebeb": sebep,
                        "Qeyd": qeyd,
                        "Emekdas_SAA": st.session_state.logged_emp_name,
                        "Emekdas_ID": st.session_state.logged_emp_id,
                        "Sistem_Vaxti": save_time
                    }
                    df_new = pd.DataFrame([new_row])
                    st.session_state.results_db = pd.concat([st.session_state.results_db, df_new], ignore_index=True)
                    st.success(f"Məlumat uğurla yadda saxlanıldı! Vaxt: {save_time}")
    
