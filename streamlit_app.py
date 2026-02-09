import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Настройка страницы
st.set_page_config(page_title="Калькулятор парных и саун", layout="wide")

# Инициализация session_state
if 'orders' not in st.session_state:
    st.session_state.orders = []
if 'current_order' not in st.session_state:
    st.session_state.current_order = {
        'client': '',
        'date': datetime.now(),
        'rooms': []
    }

# Заголовок
st.title("🛁 Калькулятор отделки парных и саун")

# Боковая панель - информация о заказе
with st.sidebar:
    st.header("Информация о заказе")
    client_name = st.text_input("Имя клиента", value=st.session_state.current_order['client'])
    order_date = st.date_input("Дата заказа", value=st.session_state.current_order['date'])
    
    st.session_state.current_order['client'] = client_name
    st.session_state.current_order['date'] = order_date
    
    st.divider()
    
    # Цены на материалы (можно редактировать)
    st.subheader("Цены на материалы")
    
    prices = {
        'vagonka_m2': st.number_input("Вагонка (₽/м²)", value=800.0, step=50.0),
        'uteplitel_m2': st.number_input("Утеплитель (₽/м²)", value=350.0, step=10.0),
        'paroizolyaciya_m2': st.number_input("Пароизоляция (₽/м²)", value=120.0, step=10.0),
        'brus_pogon': st.number_input("Брус 50x50 (₽/пог.м)", value=80.0, step=5.0),
        'polok_unit': st.number_input("Полок (₽/шт)", value=3500.0, step=100.0),
        'klyaymery_pack': st.number_input("Кляймеры упак. (₽)", value=150.0, step=10.0),
        'samorez_pack': st.number_input("Саморезы упак. (₽)", value=200.0, step=10.0),
    }
    
    st.divider()
    
    # Цены на работы
    st.subheader("Цены на работы")
    
    work_prices = {
        'montazh_m2': st.number_input("Монтаж вагонки (₽/м²)", value=500.0, step=50.0),
        'uteplenie_m2': st.number_input("Утепление (₽/м²)", value=300.0, step=10.0),
        'shlifovka_m2': st.number_input("Шлифовка (₽/м²)", value=150.0, step=10.0),
        'obrabotka_m2': st.number_input("Обработка маслом (₽/м²)", value=100.0, step=10.0),
        'polok_montazh': st.number_input("Монтаж полка (₽/шт)", value=2000.0, step=100.0),
    }

# Основная область
tab1, tab2, tab3 = st.tabs(["📝 Расчёт помещений", "💰 Итоговая смета", "💾 Сохранённые заказы"])

with tab1:
    st.header("Добавить помещение")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        room_name = st.text_input("Название помещения", placeholder="Например: Парная, Моечная, Комната отдыха")
    
    with col2:
        st.write("")  # Отступ
        st.write("")  # Отступ
    
    # Параметры помещения
    st.subheader("Размеры помещения")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        length = st.number_input("Длина (м)", min_value=0.0, value=3.0, step=0.1, key="length")
    with col2:
        width = st.number_input("Ширина (м)", min_value=0.0, value=2.5, step=0.1, key="width")
    with col3:
        height = st.number_input("Высота (м)", min_value=0.0, value=2.2, step=0.1, key="height")
    with col4:
        st.write("")
        st.write("")
        perimeter = 2 * (length + width)
        st.metric("Периметр", f"{perimeter:.2f} м")
    
    # Расчёт площадей
    floor_area = length * width
    ceiling_area = length * width
    walls_area = perimeter * height
    total_area = walls_area + ceiling_area
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Площадь пола", f"{floor_area:.2f} м²")
    with col2:
        st.metric("Площадь стен", f"{walls_area:.2f} м²")
    with col3:
        st.metric("Площадь потолка", f"{ceiling_area:.2f} м²")
    
    st.divider()
    
    # Выбор работ и материалов
    st.subheader("Материалы и работы")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Материалы:**")
        use_vagonka = st.checkbox("Вагонка на стены и потолок", value=True)
        use_uteplitel = st.checkbox("Утеплитель", value=True)
        use_paroizolyaciya = st.checkbox("Пароизоляция", value=True)
        use_obreshetka = st.checkbox("Обрешётка (брус 50x50)", value=True)
        
        polok_count = st.number_input("Количество полков (шт)", min_value=0, value=2, step=1)
    
    with col2:
        st.write("**Работы:**")
        do_montazh = st.checkbox("Монтаж вагонки", value=True)
        do_uteplenie = st.checkbox("Утепление", value=True)
        do_shlifovka = st.checkbox("Шлифовка", value=True)
        do_obrabotka = st.checkbox("Обработка маслом", value=True)
        do_polok_montazh = st.checkbox("Монтаж полков", value=True if polok_count > 0 else False)
    
    st.divider()
    
    # Расчёт материалов
    materials_cost = 0
    materials_list = []
    
    if use_vagonka:
        vagonka_area = total_area * 1.1  # +10% на подрезку
        vagonka_cost = vagonka_area * prices['vagonka_m2']
        materials_cost += vagonka_cost
        materials_list.append({
            'Материал': 'Вагонка',
            'Количество': f"{vagonka_area:.2f} м²",
            'Цена за ед.': f"{prices['vagonka_m2']:.2f} ₽",
            'Сумма': f"{vagonka_cost:.2f} ₽"
        })
    
    if use_uteplitel:
        uteplitel_area = walls_area * 1.05  # +5% на подрезку
        uteplitel_cost = uteplitel_area * prices['uteplitel_m2']
        materials_cost += uteplitel_cost
        materials_list.append({
            'Материал': 'Утеплитель',
            'Количество': f"{uteplitel_area:.2f} м²",
            'Цена за ед.': f"{prices['uteplitel_m2']:.2f} ₽",
            'Сумма': f"{uteplitel_cost:.2f} ₽"
        })
    
    if use_paroizolyaciya:
        paroiz_area = walls_area * 1.05
        paroiz_cost = paroiz_area * prices['paroizolyaciya_m2']
        materials_cost += paroiz_cost
        materials_list.append({
            'Материал': 'Пароизоляция',
            'Количество': f"{paroiz_area:.2f} м²",
            'Цена за ед.': f"{prices['paroizolyaciya_m2']:.2f} ₽",
            'Сумма': f"{paroiz_cost:.2f} ₽"
        })
    
    if use_obreshetka:
        # Обрешётка: вертикальные стойки каждые 0.5м + горизонтальные по периметру
        vertical_bars = (perimeter / 0.5) * height  # Вертикальные
        horizontal_bars = perimeter * 3  # 3 горизонтальных ряда
        total_bars = (vertical_bars + horizontal_bars) * 1.1  # +10% на подрезку
        bars_cost = total_bars * prices['brus_pogon']
        materials_cost += bars_cost
        materials_list.append({
            'Материал': 'Брус 50x50',
            'Количество': f"{total_bars:.2f} пог.м",
            'Цена за ед.': f"{prices['brus_pogon']:.2f} ₽",
            'Сумма': f"{bars_cost:.2f} ₽"
        })
    
    if polok_count > 0:
        polok_cost = polok_count * prices['polok_unit']
        materials_cost += polok_cost
        materials_list.append({
            'Материал': 'Полок',
            'Количество': f"{polok_count} шт",
            'Цена за ед.': f"{prices['polok_unit']:.2f} ₽",
            'Сумма': f"{polok_cost:.2f} ₽"
        })
    
    # Крепёж
    if use_vagonka:
        klyaymery_packs = int(total_area / 2) + 1  # 1 упаковка на 2 м²
        klyaymery_cost = klyaymery_packs * prices['klyaymery_pack']
        materials_cost += klyaymery_cost
        materials_list.append({
            'Материал': 'Кляймеры',
            'Количество': f"{klyaymery_packs} упак",
            'Цена за ед.': f"{prices['klyaymery_pack']:.2f} ₽",
            'Сумма': f"{klyaymery_cost:.2f} ₽"
        })
    
    if use_obreshetka:
        samorez_packs = int(total_area / 3) + 1  # 1 упаковка на 3 м²
        samorez_cost = samorez_packs * prices['samorez_pack']
        materials_cost += samorez_cost
        materials_list.append({
            'Материал': 'Саморезы',
            'Количество': f"{samorez_packs} упак",
            'Цена за ед.': f"{prices['samorez_pack']:.2f} ₽",
            'Сумма': f"{samorez_cost:.2f} ₽"
        })
    
    # Расчёт работ
    work_cost = 0
    work_list = []
    
    if do_montazh and use_vagonka:
        montazh_cost = total_area * work_prices['montazh_m2']
        work_cost += montazh_cost
        work_list.append({
            'Работа': 'Монтаж вагонки',
            'Объём': f"{total_area:.2f} м²",
            'Цена за ед.': f"{work_prices['montazh_m2']:.2f} ₽",
            'Сумма': f"{montazh_cost:.2f} ₽"
        })
    
    if do_uteplenie and use_uteplitel:
        uteplenie_cost = walls_area * work_prices['uteplenie_m2']
        work_cost += uteplenie_cost
        work_list.append({
            'Работа': 'Утепление',
            'Объём': f"{walls_area:.2f} м²",
            'Цена за ед.': f"{work_prices['uteplenie_m2']:.2f} ₽",
            'Сумма': f"{uteplenie_cost:.2f} ₽"
        })
    
    if do_shlifovka and use_vagonka:
        shlifovka_cost = total_area * work_prices['shlifovka_m2']
        work_cost += shlifovka_cost
        work_list.append({
            'Работа': 'Шлифовка',
            'Объём': f"{total_area:.2f} м²",
            'Цена за ед.': f"{work_prices['shlifovka_m2']:.2f} ₽",
            'Сумма': f"{shlifovka_cost:.2f} ₽"
        })
    
    if do_obrabotka and use_vagonka:
        obrabotka_cost = total_area * work_prices['obrabotka_m2']
        work_cost += obrabotka_cost
        work_list.append({
            'Работа': 'Обработка маслом',
            'Объём': f"{total_area:.2f} м²",
            'Цена за ед.': f"{work_prices['obrabotka_m2']:.2f} ₽",
            'Сумма': f"{obrabotka_cost:.2f} ₽"
        })
    
    if do_polok_montazh and polok_count > 0:
        polok_montazh_cost = polok_count * work_prices['polok_montazh']
        work_cost += polok_montazh_cost
        work_list.append({
            'Работа': 'Монтаж полков',
            'Объём': f"{polok_count} шт",
            'Цена за ед.': f"{work_prices['polok_montazh']:.2f} ₽",
            'Сумма': f"{polok_montazh_cost:.2f} ₽"
        })
    
    # Итого по помещению
    room_total = materials_cost + work_cost
    
    st.subheader("Смета по помещению")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Материалы", f"{materials_cost:,.2f} ₽")
    with col2:
        st.metric("🔨 Работы", f"{work_cost:,.2f} ₽")
    with col3:
        st.metric("📊 ИТОГО", f"{room_total:,.2f} ₽")
    
    # Показать детализацию
    with st.expander("📋 Детализация материалов"):
        if materials_list:
            df_materials = pd.DataFrame(materials_list)
            st.dataframe(df_materials, use_container_width=True, hide_index=True)
        else:
            st.info("Материалы не выбраны")
    
    with st.expander("🔧 Детализация работ"):
        if work_list:
            df_work = pd.DataFrame(work_list)
            st.dataframe(df_work, use_container_width=True, hide_index=True)
        else:
            st.info("Работы не выбраны")
    
    # Кнопка добавления помещения
    st.divider()
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("➕ Добавить помещение в заказ", type="primary", use_container_width=True):
            if not room_name:
                st.error("Укажите название помещения!")
            else:
                room_data = {
                    'name': room_name,
                    'dimensions': {
                        'length': length,
                        'width': width,
                        'height': height,
                        'perimeter': perimeter,
                        'floor_area': floor_area,
                        'walls_area': walls_area,
                        'ceiling_area': ceiling_area,
                        'total_area': total_area
                    },
                    'materials': materials_list,
                    'work': work_list,
                    'materials_cost': materials_cost,
                    'work_cost': work_cost,
                    'total': room_total
                }
                st.session_state.current_order['rooms'].append(room_data)
                st.success(f"✅ Помещение '{room_name}' добавлено!")
                st.rerun()
    
    with col2:
        if st.button("🗑️ Очистить форму", use_container_width=True):
            st.rerun()

with tab2:
    st.header("Итоговая смета по заказу")
    
    if not st.session_state.current_order['rooms']:
        st.info("📝 Добавьте помещения в заказ на вкладке 'Расчёт помещений'")
    else:
        # Информация о заказе
        st.subheader(f"Клиент: {st.session_state.current_order['client'] or 'Не указан'}")
        st.write(f"Дата: {st.session_state.current_order['date'].strftime('%d.%m.%Y')}")
        
        st.divider()
        
        # Список помещений
        total_materials = 0
        total_work = 0
        
        for idx, room in enumerate(st.session_state.current_order['rooms']):
            with st.expander(f"🏠 {room['name']} — {room['total']:,.2f} ₽", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Размеры:**")
                    st.write(f"- Длина: {room['dimensions']['length']} м")
                    st.write(f"- Ширина: {room['dimensions']['width']} м")
                    st.write(f"- Высота: {room['dimensions']['height']} м")
                    st.write(f"- Площадь отделки: {room['dimensions']['total_area']:.2f} м²")
                
                with col2:
                    st.write("**Стоимость:**")
                    st.write(f"- Материалы: {room['materials_cost']:,.2f} ₽")
                    st.write(f"- Работы: {room['work_cost']:,.2f} ₽")
                    st.write(f"- **ИТОГО: {room['total']:,.2f} ₽**")
                
                col1, col2, col3 = st.columns([3, 3, 1])
                
                with col1:
                    if room['materials']:
                        st.write("**Материалы:**")
                        df_mat = pd.DataFrame(room['materials'])
                        st.dataframe(df_mat, use_container_width=True, hide_index=True)
                
                with col2:
                    if room['work']:
                        st.write("**Работы:**")
                        df_wrk = pd.DataFrame(room['work'])
                        st.dataframe(df_wrk, use_container_width=True, hide_index=True)
                
                with col3:
                    st.write("")
                    st.write("")
                    if st.button("❌", key=f"del_{idx}", help="Удалить помещение"):
                        st.session_state.current_order['rooms'].pop(idx)
                        st.rerun()
            
            total_materials += room['materials_cost']
            total_work += room['work_cost']
        
        # Итого по заказу
        st.divider()
        
        grand_total = total_materials + total_work
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Материалы всего", f"{total_materials:,.2f} ₽")
        with col2:
            st.metric("🔨 Работы всего", f"{total_work:,.2f} ₽")
        with col3:
            st.metric("📊 ИТОГО", f"{grand_total:,.2f} ₽")
        with col4:
            st.write("")
            st.write("")
        
        st.divider()
        
        # Кнопки действий
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Сохранить заказ", type="primary", use_container_width=True):
                if not st.session_state.current_order['client']:
                    st.error("Укажите имя клиента!")
                else:
                    order_copy = st.session_state.current_order.copy()
                    order_copy['grand_total'] = grand_total
                    order_copy['total_materials'] = total_materials
                    order_copy['total_work'] = total_work
                    st.session_state.orders.append(order_copy)
                    
                    # Очистить текущий заказ
                    st.session_state.current_order = {
                        'client': '',
                        'date': datetime.now(),
                        'rooms': []
                    }
                    
                    st.success("✅ Заказ сохранён!")
                    st.rerun()
        
        with col2:
            # Экспорт в Excel
            if st.button("📥 Скачать в Excel", use_container_width=True):
                # Создаём Excel файл
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    # Общая информация
                    summary_data = {
                        'Клиент': [st.session_state.current_order['client']],
                        'Дата': [st.session_state.current_order['date'].strftime('%d.%m.%Y')],
                        'Материалы всего': [f"{total_materials:,.2f} ₽"],
                        'Работы всего': [f"{total_work:,.2f} ₽"],
                        'ИТОГО': [f"{grand_total:,.2f} ₽"]
                    }
                    df_summary = pd.DataFrame(summary_data)
                    df_summary.to_excel(writer, sheet_name='Общая информация', index=False)
                    
                    # По каждому помещению
                    for room in st.session_state.current_order['rooms']:
                        sheet_name = room['name'][:31]  # Excel ограничение на длину имени листа
                        
                        # Материалы
                        if room['materials']:
                            df_materials = pd.DataFrame(room['materials'])
                            df_materials.to_excel(writer, sheet_name=sheet_name, startrow=0, index=False)
                        
                        # Работы
                        if room['work']:
                            df_work = pd.DataFrame(room['work'])
                            start_row = len(room['materials']) + 3 if room['materials'] else 0
                            df_work.to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=False)
                
                excel_data = output.getvalue()
                
                st.download_button(
                    label="💾 Скачать Excel",
                    data=excel_data,
                    file_name=f"smeta_{st.session_state.current_order['client']}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        with col3:
            if st.button("🗑️ Очистить заказ", use_container_width=True):
                st.session_state.current_order = {
                    'client': '',
                    'date': datetime.now(),
                    'rooms': []
                }
                st.rerun()

with tab3:
    st.header("Сохранённые заказы")
    
    if not st.session_state.orders:
        st.info("📭 Нет сохранённых заказов")
    else:
        for idx, order in enumerate(st.session_state.orders):
            with st.expander(f"📋 {order['client']} — {order['date'].strftime('%d.%m.%Y')} — {order['grand_total']:,.2f} ₽"):
                st.write(f"**Количество помещений:** {len(order['rooms'])}")
                st.write(f"**Материалы:** {order['total_materials']:,.2f} ₽")
                st.write(f"**Работы:** {order['total_work']:,.2f} ₽")
                st.write(f"**ИТОГО:** {order['grand_total']:,.2f} ₽")
                
                st.write("**Помещения:**")
                for room in order['rooms']:
                    st.write(f"- {room['name']}: {room['total']:,.2f} ₽")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🔄 Загрузить в работу", key=f"load_{idx}"):
                        st.session_state.current_order = order.copy()
                        st.success("✅ Заказ загружен!")
                        st.rerun()
                
                with col2:
                    if st.button("❌ Удалить", key=f"delete_{idx}"):
                        st.session_state.orders.pop(idx)
                        st.rerun()

# Футер
st.divider()
st.caption("💡 Совет: Сохраняйте цены на материалы и работы в боковой панели для быстрого расчёта")
