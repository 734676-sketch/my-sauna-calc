import streamlit as st
import pandas as pd

st.set_page_config(page_title="Калькулятор отделки бань", layout="wide")

st.title("🏗 Расчет отделки парной")

# --- БЛОК 1: ПАРАМЕТРЫ ПОМЕЩЕНИЯ ---
st.header("1. Размеры помещения (м)")
col1, col2, col3 = st.columns(3)
with col1:
    depth = st.number_input("Глубина (м)", value=2.0, step=0.1)
with col2:
    width = st.number_input("Ширина (м)", value=2.5, step=0.1)
with col3:
    height = st.number_input("Высота (м)", value=2.2, step=0.1)

s_walls = 2 * (depth + width) * height
s_ceiling = depth * width
s_total = s_walls + s_ceiling

st.info(#33
    f"**Площадь стен:** {s_walls:.2f} м² | "
    f"**Площадь потолка:** {s_ceiling:.2f} м² | "
    f"**Итого под отделку:** {s_total:.2f} м²"
)

# --- БЛОК 2: РАСЧЕТ ВАГОНКИ (Тип В) ---
st.header("2. Расчет вагонки (материалы с формулами)")
margin = st.slider("Запас на подрезку (%)", 0, 20, 10) / 100

num_types = st.radio("Сколько видов вагонки используем?", [1, 2, 3], horizontal=True)

linings = []
total_allocated_area = 0

for i in range(num_types):
    st.subheader(f"Вид вагонки №{i+1}")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        name = st.text_input(f"Название {i+1}", value=f"Вагонка {i+1}")
    with c2:
        l_width = st.number_input(f"Ширина доски (мм)", value=90, key=f"w{i}") / 1000
    with c3:
        percent = st.number_input(f"% от общей площади", value=int(100/num_types), key=f"p{i}") / 100
    with c4:
        price = st.number_input(f"Цена за м² (руб)", value=1500, key=f"pr{i}")
    
    # Расчет для конкретного вида
    area_needed = s_total * percent * (1 + margin)
    cost = area_needed * price
    linings.append({"Название": name, "Площадь (с запасом)": round(area_needed, 2), "Сумма": round(cost, 2)})

df_linings = pd.DataFrame(linings)
st.table(df_linings)

# --- БЛОК 3: РАБОТЫ И ФИКСИРОВАННЫЕ ТОВАРЫ (Тип А и Б) ---
st.header("3. Дополнительные расходы")
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("А) Работы")
    work_list = st.text_area("Список работ и цены (через запятую: Работа, Цена)", 
                             "Монтаж каркаса, 500\nОбшивка вагонкой, 800\nШлифовка, 200")

with col_b:
    st.subheader("Б) Готовые товары")
    fixed_list = st.text_area("Материалы (через запятую: Название, Цена)", 
                              "Дверь стеклянная, 15000\nПечь, 45000\nКамни (уп), 1200")

# --- ИТОГО ---
st.divider()
total_linings = df_linings["Сумма"].sum()
st.subheader(f"Предварительная стоимость материалов (вагонка): {total_linings:,.2f} руб.")

st.caption("Этот расчет можно сохранить в PDF или отправить ссылкой клиенту.")
