import streamlit as st
import google.generativeai as genai
import time

# ═══════════════════════════════════════════════════════
# إعدادات الصفحة
# ═══════════════════════════════════════════════════════
st.set_page_config(
    page_title="نظام استكشاف منهج النبي ﷺ",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════
# CSS للتنسيق العربي (RTL)
# ═══════════════════════════════════════════════════════
st.markdown("""
<style>
    /* الاتجاه من اليمين لليسار */
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: 'Tajawal', 'Cairo', 'Amiri', sans-serif;
    }
    
    /* العنوان الرئيسي */
    .main-title {
        background: linear-gradient(135deg, #0d4d3d 0%, #1a6b52 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .main-title h1 {
        margin: 0;
        font-size: 28px;
        font-weight: bold;
    }
    .main-title p {
        margin: 8px 0 0 0;
        font-size: 16px;
        opacity: 0.9;
    }
    
    /* بطاقة النتيجة */
    .result-card {
        background: #f8f9fa;
        border-right: 5px solid #0d4d3d;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .result-card h3 {
        color: #0d4d3d;
        margin-top: 0;
        border-bottom: 2px solid #d4af37;
        padding-bottom: 8px;
    }
    
    /* حقول الثابت والمتغير */
    .field-box {
        background: white;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-right: 4px solid #d4af37;
    }
    .field-label {
        color: #0d4d3d;
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 8px;
    }
    .field-content {
        color: #333;
        font-size: 15px;
        line-height: 1.7;
    }
    
    /* تنبيه */
    .disclaimer {
        background: #fff3cd;
        border-right: 4px solid #ffc107;
        padding: 12px;
        border-radius: 8px;
        margin-top: 20px;
        color: #856404;
        font-size: 14px;
    }
    
    /* الأزرار */
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
    
    /* الشريط الجانبي */
    .css-1d391kg {
        background: #f0f4f2;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# البرومبت المركّب (System Prompt)
# ═══════════════════════════════════════════════════════
SYSTEM_PROMPT = """
أنت محلل متخصص في منهج النبي ﷺ. مهمتك تحليل الأحاديث النبوية
لاستخراج المنهج من مركزه، لا من أبوابه الفقهية.

═══════════════════════════════════════════════
الإطار الفكري
═══════════════════════════════════════════════

المبدأ الأساسي:
النبي ﷺ شخصية واحدة، عاش في زمن واحد، ومكان واحد.
فإذا ذكر متغيرًا، غالبًا يخدم ثابتًا.
وإذا ذكر ثابتًا، غالبًا يخدم غاية.
الغاية الكبرى: رضا الله والاهتداء بهديه.

═══════════════════════════════════════════════
الأبعاد العشرة
═══════════════════════════════════════════════

01. المعرفة — كيف نعرف؟ ما مصدر علمنا؟
02. القول — ماذا نقول؟ كيف نتكلم؟
03. الفعل — ماذا نفعل؟ كيف نعمل؟
04. الذات — كيف نتعامل مع أنفسنا؟
05. الآخر — كيف نتعامل مع عموم الناس؟
06. الزمن — كيف ننظم وقتنا وأعمارنا؟
07. المال — كيف نكسب المال وننفقه؟
08. المقدس — ما طبيعة علاقتنا بالله؟
09. السلطة — كيف نحكم ونتحكم وندير؟
10. الجسد — كيف نعتني بأجسادنا وصحتنا؟

═══════════════════════════════════════════════
الخطوات السبع
═══════════════════════════════════════════════

1. التحقق من المصدر.
2. التصنيف على الأبعاد.
3. استخراج الثابت.
4. استخراج المتغير.
5. تحديد الوظيفة (تأسيس/تقييد/توسيع/تصحيح).
6. ربط العلاقات.
7. استخلاص الغاية.

═══════════════════════════════════════════════
شكل المخرج
═══════════════════════════════════════════════

أخرج الإجابة بهذا التنسيق بالضبط:

**المصدر:** [الكتاب والرقم والراوي]

**نص الحديث:** [النص]

**التصنيف:**
- البُعد الأساسي: [اسم]
- أبعاد ثانوية: [أسماء]

**الثابت:**
[ما لا يتغير]

**المتغير:**
[ما يتغير]

**الوظيفة:**
[تأسيس / تقييد / توسيع / تصحيح]

**العلاقات:**
[بأي أبعاد أخرى يرتبط]

**الغاية:**
[ما أراده النبي ﷺ]

**الفائدة العملية:**
[كيف يستفيد المسلم]

═══════════════════════════════════════════════
ضوابط السلامة (إلزامية)
═══════════════════════════════════════════════

1. لا حكم على الحديث (لا تصحّح، لا تضعّف).
2. لا فتوى (أحل للمختصين).
3. لا هلوسة (لا تخترع حديثًا أو راويًا).
4. الإحالة الإلزامية للمصدر.
5. التمييز بين الثابت والمتغير.

═══════════════════════════════════════════════
قواعد الأسلوب
═══════════════════════════════════════════════

- العربية الفصحى المبسّطة.
- تعليمي، محترم، موضوعي.
- لا تحيز لمذهب.
- إذا وُجد خلاف، اعرضه بحياد.

═══════════════════════════════════════════════
تنبيه
═══════════════════════════════════════════════

إذا لم تكن متأكدًا من مصدر الحديث، قل ذلك بوضوح.
إذا كان الحديث خارج المصادر المعتمدة، نبّه على ذلك.
"""

# ═══════════════════════════════════════════════════════
# الأمثلة الجاهزة
# ═══════════════════════════════════════════════════════
EXAMPLES = {
    "حديث الرفق": "إن الله رفيق يحب الرفق في الأمر كله",
    "حديث النيات": "إنما الأعمال بالنيات وإنما لكل امرئ ما نوى",
    "حديث الكلمة الطيبة": "من كان يؤمن بالله واليوم الآخر فليقل خيرًا أو ليصمت",
    "حديث الجسد": "إن لجسدك عليك حقًا",
    "حديث الصدق": "عليكم بالصدق فإن الصدق يهدي إلى البر"
}

# ═══════════════════════════════════════════════════════
# دالة الاتصال بـ Gemini
# ═══════════════════════════════════════════════════════
def analyze_hadith(hadith_text, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
        response = model.generate_content(hadith_text)
        return response.text, None
    except Exception as e:
        return None, str(e)

# ═══════════════════════════════════════════════════════
# الواجهة
# ═══════════════════════════════════════════════════════

# العنوان
st.markdown("""
<div class="main-title">
    <h1>🕌 نظام استكشاف منهج النبي ﷺ</h1>
    <p>خريطة إشعاعية للثوابت والمتغيرات في الأحاديث النبوية</p>
</div>
""", unsafe_allow_html=True)

# الشريط الجانبي — أمثلة جاهزة
with st.sidebar:
    st.markdown("### 📚 أمثلة جاهزة")
    st.markdown("اضغط على أي مثال لتجربته:")
    
    if "selected_example" not in st.session_state:
        st.session_state.selected_example = ""
    
    for name, text in EXAMPLES.items():
        if st.button(f"▪ {name}", key=name):
            st.session_state.selected_example = text
    
    st.markdown("---")
    st.markdown("### ℹ️ عن النظام")
    st.markdown("""
    نظام ذكي يحلل الأحاديث النبوية وفق عشرة أبعاد،
    لفصل الثوابت عن المتغيرات.
    
    **المصادر المعتمدة:**
    - dorar.net
    - shamela.ws
    """)

# حقل الإدخال
st.markdown("### 🔍 أدخل نص الحديث للتحليل")

hadith_input = st.text_area(
    "نص الحديث:",
    value=st.session_state.selected_example,
    height=120,
    placeholder="اكتب نص الحديث هنا، أو اختر مثالًا من الشريط الجانبي..."
)

# زر التحليل
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_button = st.button("🚀 تحليل الحديث", use_container_width=True)

# ═══════════════════════════════════════════════════════
# التنفيذ
# ═══════════════════════════════════════════════════════
if analyze_button:
    if not hadith_input.strip():
        st.warning("⚠️ الرجاء إدخال نص حديث أولًا.")
    else:
        # قراءة مفتاح API
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            st.error("❌ لم يتم تكوين مفتاح API. تأكد من إضافة GEMINI_API_KEY في إعدادات Secrets.")
            st.stop()
        
        # عرض التحميل
        with st.spinner("⏳ جاري تحليل الحديث..."):
            result, error = analyze_hadith(hadith_input, api_key)
        
        if error:
            st.error(f"❌ حدث خطأ أثناء التحليل:\n\n{error}")
        else:
            st.success("✅ تم التحليل بنجاح")
            st.markdown("---")
            st.markdown("### 📋 بطاقة الموقف")
            st.markdown(result)
            
            # تنبيه
            st.markdown("""
            <div class="disclaimer">
                ⚠️ <strong>تنبيه:</strong> هذا النظام أداة استكشاف علمي وبحثي،
                وليس مصدر فتوى. جميع المخرجات تحتاج مراجعة المتخصص الشرعي.
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
