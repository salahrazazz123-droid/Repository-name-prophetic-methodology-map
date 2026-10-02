import streamlit as st
import google.generativeai as genai

# ═══════════════════════════════════════════════════════
st.set_page_config(
    page_title="نظام استكشاف منهج النبي ﷺ",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════
# CSS — التنسيق العربي
# ═══════════════════════════════════════════════════════
st.markdown("""
<style>
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: 'Tajawal', 'Cairo', 'Amiri', sans-serif;
    }
    .main-title {
        background: linear-gradient(135deg, #0d4d3d 0%, #1a6b52 100%);
        color: white;
        padding: 25px;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .main-title h1 { margin: 0; font-size: 26px; }
    .main-title p { margin: 8px 0 0 0; font-size: 15px; opacity: 0.9; }
    
    .idea-box {
        background: #f8f9fa;
        border-right: 5px solid #0d4d3d;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        line-height: 1.9;
    }
    
    .dimension-card {
        background: linear-gradient(135deg, #0d4d3d 0%, #1a6b52 100%);
        color: white;
        padding: 12px 10px;
        border-radius: 10px;
        text-align: center;
        margin: 4px 0;
        font-size: 13px;
        font-weight: bold;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }
    .dimension-card-active {
        background: linear-gradient(135deg, #d4af37 0%, #b8941e 100%);
        color: #0d4d3d;
        padding: 12px 10px;
        border-radius: 10px;
        text-align: center;
        margin: 4px 0;
        font-size: 13px;
        font-weight: bold;
        box-shadow: 0 3px 10px rgba(212,175,55,0.4);
        border: 2px solid #0d4d3d;
    }
    
    .function-highlight {
        background: linear-gradient(135deg, #d4af37 0%, #b8941e 100%);
        color: #0d4d3d;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin: 15px 0;
        font-size: 17px;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(212,175,55,0.3);
    }
    
    .golden-summary {
        background: linear-gradient(135deg, #0d4d3d 0%, #1a6b52 100%);
        color: white;
        padding: 22px;
        border-radius: 14px;
        text-align: center;
        margin: 20px 0;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0 6px 20px rgba(13,77,61,0.4);
        border: 3px solid #d4af37;
    }
    
    .disclaimer {
        background: #fff3cd;
        border-right: 4px solid #ffc107;
        padding: 12px;
        border-radius: 8px;
        margin-top: 20px;
        color: #856404;
        font-size: 14px;
    }
    
    .step-card {
        background: #f8f9fa;
        border-right: 4px solid #d4af37;
        border-radius: 10px;
        padding: 18px;
        margin: 12px 0;
    }
    .step-card h4 {
        color: #0d4d3d;
        margin-top: 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #0d4d3d 0%, #1a6b52 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 30px;
        font-size: 16px;
        font-weight: bold;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #1a6b52 0%, #0d4d3d 100%);
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# الأبعاد العشرة
# ═══════════════════════════════════════════════════════
DIMENSIONS = [
    {"id": 1, "name": "المعرفة", "question": "كيف نعرف؟ وما مصدر علمنا؟",
     "constants": "الوحي، العقل، الصدق في النقل، طلب العلم",
     "variables": "طرق التعليم، اللغة، الأدوات، المستوى"},
    {"id": 2, "name": "القول", "question": "ماذا نقول؟ وكيف نتكلم؟",
     "constants": "الصدق، عدم الغيبة، الوضوح، قول الخير أو الصمت",
     "variables": "اللغة، اللهجة، الأسلوب، الصوت، الجمهور"},
    {"id": 3, "name": "الفعل", "question": "ماذا نفعل؟ وكيف نعمل؟",
     "constants": "الإتقان، الإخلاص، المبادرة، عدم التسويف",
     "variables": "نوع العمل، الوقت، القدرة، الأدوات"},
    {"id": 4, "name": "الذات", "question": "كيف نتعامل مع أنفسنا؟",
     "constants": "الإخلاص، المحاسبة، التواضع، التوبة",
     "variables": "طرق المحاسبة، الوقت، الشكل"},
    {"id": 5, "name": "الآخر", "question": "كيف نتعامل مع الناس؟",
     "constants": "الرحمة، العدل، حسن الجوار، العفو",
     "variables": "أشكال الرحمة، الحدود، الأساليب"},
    {"id": 6, "name": "الزمن", "question": "كيف ننظم وقتنا؟",
     "constants": "الآخرة، اغتنام الوقت، عدم التسويف",
     "variables": "تنظيم الوقت، الأولويات، الاستعداد"},
    {"id": 7, "name": "المال", "question": "كيف نكسب وننفق؟",
     "constants": "الحلال، الزكاة، عدم الإسراف، عدم الاحتكار",
     "variables": "طرق الكسب، طرق الإنفاق، المقدار"},
    {"id": 8, "name": "المقدس", "question": "ما علاقتنا بالله؟",
     "constants": "التوحيد، الوحي، الرسالة، الآخرة",
     "variables": "أشكال العبادة، الأماكن، الأوقات"},
    {"id": 9, "name": "السلطة", "question": "كيف نحكم ونتحكم؟",
     "constants": "الأمانة، العدل، الشورى، عدم الاستبداد",
     "variables": "شكل الحكم، طرق التعيين، الأدوات"},
    {"id": 10, "name": "الجسد", "question": "كيف نعتني بأجسادنا؟",
     "constants": "الطهارة، الاعتدال، عدم إيذاء الجسد",
     "variables": "أنواع الطعام، أشكال الرياضة، اللباس"},
]

# ═══════════════════════════════════════════════════════
# البرومبت المركّب
# ═══════════════════════════════════════════════════════
SYSTEM_PROMPT = """
أنت محلل متخصص في منهج النبي ﷺ. مهمتك تحليل الأحاديث النبوية
لاستخراج المنهج من مركزه، لا من أبوابه الفقهية.

المبدأ الأساسي:
النبي ﷺ شخصية واحدة، عاش في زمن واحد ومكان واحد.
فإذا ذكر متغيرًا، غالبًا يخدم ثابتًا.
وإذا ذكر ثابتًا، غالبًا يخدم غاية.
الغاية الكبرى: رضا الله والاهتداء بهديه.

الأبعاد العشرة للتصنيف:
01. المعرفة — كيف نعرف؟
02. القول — ماذا نقول؟
03. الفعل — ماذا نفعل؟
04. الذات — كيف نتعامل مع أنفسنا؟
05. الآخر — كيف نتعامل مع الناس؟
06. الزمن — كيف ننظم وقتنا؟
07. المال — كيف نكسب وننفق؟
08. المقدس — ما علاقتنا بالله؟
09. السلطة — كيف نحكم؟
10. الجسد — كيف نعتني بأجسادنا؟

أخرج الإجابة بهذا التنسيق بالضبط:

**المصدر:** [الكتاب والرقم والراوي]

**نص الحديث:** [النص]

**التصنيف:**
- البُعد الأساسي: [اسم]
- أبعاد ثانوية: [أسماء]

**الثابت:** [ما لا يتغير]

**المتغير:** [ما يتغير]

**الوظيفة:** [تأسيس قاعدة / تقييد / توسيع / تصحيح - واشرح]

**العلاقات:** [بأي أبعاد أخرى يرتبط]

**الغاية:** [ما أراده النبي ﷺ]

**الفائدة العملية:** [كيف يستفيد المسلم]

**الخلاصة الذهبية:** جملة واحدة مركزة (10-15 كلمة)
تُلخّص الفهم المطلوب، بطريقة تسهّل الحفظ والتطبيق الفوري.

ضوابط السلامة (إلزامية):
1. لا حكم على الحديث (لا تصحّح، لا تضعّف).
2. لا فتوى.
3. لا هلوسة.
4. الإحالة الإلزامية للمصدر.
5. التمييز بين الثابت والمتغير.
6. إذا لم تكن متأكدًا من المصدر، قل ذلك بوضوح.
"""

# ═══════════════════════════════════════════════════════
# الأمثلة
# ═══════════════════════════════════════════════════════
EXAMPLES = {
    "حديث الرفق": "إن الله رفيق يحب الرفق في الأمر كله",
    "حديث النيات": "إنما الأعمال بالنيات وإنما لكل امرئ ما نوى",
    "حديث الكلمة الطيبة": "من كان يؤمن بالله واليوم الآخر فليقل خيرًا أو ليصمت",
    "حديث الجسد": "إن لجسدك عليك حقًا",
    "حديث الصدق": "عليكم بالصدق فإن الصدق يهدي إلى البر"
}

# ═══════════════════════════════════════════════════════
# دالة الاتصال بـ Gemini (مع Fallback)
# ═══════════════════════════════════════════════════════
def analyze_hadith(hadith_text, api_key):
    models_to_try = [
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash",
        "gemini-2.5-flash",
    ]
    last_error = None
    for model_name in models_to_try:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=SYSTEM_PROMPT
            )
            response = model.generate_content(hadith_text)
            return response.text, None
        except Exception as e:
            last_error = str(e)
            if "429" in last_error or "quota" in last_error.lower():
                continue
            return None, last_error
    return None, "⚠️ انتهت الحصص المجانية لجميع الموديلات. الرجاء المحاولة بعد قليل."

# ═══════════════════════════════════════════════════════
# التنقل
# ═══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🧭 التنقل")
    page = st.radio(
        "اختر الصفحة:",
        ["🏠 الرئيسية", "📖 دليل الاستخدام", "🗺️ الأبعاد العشرة", "🔍 التحليل"],
        label_visibility="collapsed"
    )
    st.markdown("---")

# ═══════════════════════════════════════════════════════
# الصفحة 1: الرئيسية
# ═══════════════════════════════════════════════════════
if page == "🏠 الرئيسية":
    st.markdown("""
    <div class="main-title">
        <h1>🕌 نظام استكشاف منهج النبي ﷺ</h1>
        <p>خريطة إشعاعية للثوابت والمتغيرات في الأحاديث النبوية</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="idea-box">
    <h3 style="color:#0d4d3d; margin-top:0;">🎯 الفكرة الأساسية</h3>
    بناء خريطة إشعاعية للأحاديث النبوية عبر عشرة أبعاد، 
    تحت كل بُعد ثوابت ومتغيرات، لجعل المنهج يُفهم من 
    مركز صاحبه ﷺ، فيُحمى الثابت من التحريف، والمتغير 
    من التقديس، والمنهج من أن يخدم سوء الفهم الشخصي.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🗺️ الأبعاد العشرة")
    st.markdown("كل بُعد يمثل غرفة في بيت كبير. تحت كل بُعد ثوابت ومتغيرات.")
    
    for i in range(0, 10, 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(DIMENSIONS):
                d = DIMENSIONS[idx]
                with col:
                    st.markdown(f"""
                    <div class="dimension-card">
                        {d['id']:02d}. {d['name']}<br>
                        <span style="font-size:11px; opacity:0.85;">{d['question']}</span>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    <div class="idea-box">
    <h3 style="color:#0d4d3d; margin-top:0;">🔑 الفرق عن الترتيب التقليدي</h3>
    
    <b>الترتيب الشائع (خطي):</b><br>
    • باب ثم باب — يحتاج قراءة الكتاب كاملًا للفهم.<br>
    • يصعب الرؤية الشاملة.<br><br>
    
    <b>الترتيب الإشعاعي (حلقي):</b><br>
    • مركز ثم حلقات — يكشف العلاقات العميقة.<br>
    • يميز الثابت من المتغير.<br>
    • يسهّل الرؤية الشاملة.<br>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("🚀 ابدأ الآن — انتقل إلى صفحة **🔍 التحليل** من القائمة الجانبية.")

# ═══════════════════════════════════════════════════════
# الصفحة 2: دليل الاستخدام
# ═══════════════════════════════════════════════════════
elif page == "📖 دليل الاستخدام":
    st.markdown("""
    <div class="main-title">
        <h1>📖 دليل الاستخدام</h1>
        <p>كيف تستخدم النظام للفهم الصحيح؟</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="idea-box">
    <h3 style="color:#0d4d3d; margin-top:0;">🎯 الفكرة ليست "تصنيف أحاديث"</h3>
    بل بناء <b>هيكل فهم</b> يجعل:<br><br>
    • <b>الثابت</b> ظاهرًا محميًا.<br>
    • <b>المتغير</b> خادمًا لا مخدومًا.<br>
    • <b>المنهج</b> متصلًا بغايته.<br>
    • فهم المنهج من <b>مركز النبي ﷺ</b> — أي من غايته.<br><br>
    <i>لأن بعض الناس فهموا المنهج من مركز أنفسهم 
    (عاداتهم، مصالحهم، فهمهم الجزئي).</i>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📚 المنهجية السبع خطوات")
    
    steps = [
        ("1", "التعريف", "ديننا له ثوابت (لا تتغير) ومتغيرات (تتغير). الثوابت أصل، والمتغيرات تطبيق.", "الثابت: الصدق. المتغير: كيف نصدق؟"),
        ("2", "التمييز", "نسأل 3 أسئلة: هل يتغير بتغير الزمان؟ إذا أزلناه هل يبقى الدين؟ هل هو في المركز أم الهامش؟", "اللباس: الثابت (الستر)، المتغير (نوعه، لونه)"),
        ("3", "الحذف", "لنتأكد، لنحذف عنصرًا ونرى: هل يبقى الدين؟", "احذف الصلاة → لا يبقى الدين. احذف عدد الركعات → يبقى الدين."),
        ("4", "الضغط", "نختبر أنفسنا تحت الضغط: الغضب، الخوف، الشهوة، الفقد.", "عند الغضب: الثابت (لا نظلم)، المتغير (كيف نعبر)"),
        ("5", "الكتابة", "نكتب دستورنا: ما ثوابتنا؟ ما متغيراتنا؟", "التوحيد ثابت. شكل المسجد متغير."),
        ("6", "الحياة", "نعيش الثوابت، ونبدّل المتغيرات حسب زماننا ومكاننا.", "الصلاة ثابتة. نصلي في المسجد، البيت، العمل، السفر."),
        ("7", "التعليم", "نعلّم غيرنا: ما الثابت؟ ما المتغير؟ وكيف يفرّقون؟", "علّم ابنك: الصدق ثابت، طريقة الكلام متغيرة."),
    ]
    
    for num, title, content, example in steps:
        st.markdown(f"""
        <div class="step-card">
            <h4>الخطوة {num}: {title}</h4>
            <p>{content}</p>
            <p style="background:#e8f0ec; padding:10px; border-radius:6px; font-size:14px;">
            <b>مثال:</b> {example}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    <div class="idea-box">
    <h3 style="color:#0d4d3d; margin-top:0;">🌟 لماذا هذا مهم؟</h3>
    النبي ﷺ <b>شخصية واحدة</b>، عاش في زمن واحد ومكان واحد.<br><br>
    لذلك:<br>
    • إذا ذكر <b>متغيرًا</b> → غالبًا يخدم <b>ثابتًا</b>.<br>
    • إذا ذكر <b>ثابتًا</b> → غالبًا لتحقيق <b>غاية</b>.<br><br>
    <b>الفائدة الكبرى:</b> نستطيع استخراج المتغيرات التي تسبب 
    الشبهات أو سوء الفهم، فنوضحها ونعالجها بإشراف علماء الدين.
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# الصفحة 3: الأبعاد العشرة
# ═══════════════════════════════════════════════════════
elif page == "🗺️ الأبعاد العشرة":
    st.markdown("""
    <div class="main-title">
        <h1>🗺️ الأبعاد العشرة</h1>
        <p>تغطي كافة مجالات حياة الإنسان دون استثناء</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="idea-box">
    <b>لماذا عشرة أبعاد؟</b><br>
    لأن حياة الإنسان كلها تدور حول عشرة أمور. 
    هذه الأبعاد تغطي كل شيء. لا يخرج عنها شيء.
    </div>
    """, unsafe_allow_html=True)
    
    for d in DIMENSIONS:
        with st.expander(f"**{d['id']:02d}. {d['name']}** — {d['question']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="function-highlight" style="font-size:14px; padding:15px;">
                ⚓ <b>الثوابت</b><br>
                {d['constants']}
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="idea-box" style="font-size:14px;">
                🔄 <b>المتغيرات</b><br>
                {d['variables']}
                </div>
                """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# الصفحة 4: التحليل
# ═══════════════════════════════════════════════════════
else:
    st.markdown("""
    <div class="main-title">
        <h1>🔍 تحليل الأحاديث</h1>
        <p>أدخل نص الحديث، وستحصل على بطاقة موقف كاملة</p>
    </div>
    """, unsafe_allow_html=True)
    
    if "selected_example" not in st.session_state:
        st.session_state.selected_example = ""
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📚 أمثلة جاهزة")
        for name, text in EXAMPLES.items():
            if st.button(f"▪ {name}", key=name):
                st.session_state.selected_example = text
    
    hadith_input = st.text_area(
        "نص الحديث:",
        value=st.session_state.selected_example,
        height=100,
        placeholder="اكتب نص الحديث، أو اختر مثالًا من الشريط الجانبي..."
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button("🚀 تحليل الحديث", use_container_width=True)
    
    if analyze_button:
        if not hadith_input.strip():
            st.warning("⚠️ الرجاء إدخال نص حديث أولًا.")
        else:
            try:
                api_key = st.secrets["GEMINI_API_KEY"]
            except Exception:
                st.error("❌ لم يتم تكوين GEMINI_API_KEY في Secrets.")
                st.stop()
            
            with st.spinner("⏳ جاري تحليل الحديث..."):
                result, error = analyze_hadith(hadith_input, api_key)
            
            if error:
                st.error(f"❌ خطأ:\n\n{error}")
            else:
                st.success("✅ تم التحليل بنجاح")
                st.markdown("---")
                
                st.markdown("#### 🗺️ الموقع على الخريطة الإشعاعية")
                
                cols = st.columns(5)
                for i, d in enumerate(DIMENSIONS):
                    with cols[i % 5]:
                        is_active = d['name'] in result
                        if is_active:
                            st.markdown(f"""
                            <div class="dimension-card-active">
                                {d['id']:02d}. {d['name']}
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="dimension-card" style="opacity:0.4;">
                                {d['id']:02d}. {d['name']}
                            </div>
                            """, unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("### 📋 بطاقة الموقف")
                st.markdown(result)
                
                st.markdown("""
                <div class="disclaimer">
                    ⚠️ <strong>تنبيه:</strong> هذا النظام أداة استكشاف 
                    علمي وبحثي، وليس مصدر فتوى. جميع المخرجات تحتاج 
                    مراجعة المتخصص الشرعي.
                </div>
                """, unsafe_allow_html=True)

# تذييل
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 13px; padding: 20px;">
    تحدي الذكاء الاصطناعي في خدمة المحتوى الإسلامي 2026 — المسار الرابع<br>
    <strong>صلاح رزاز</strong> | مشاركة فردية
</div>
""", unsafe_allow_html=True)
