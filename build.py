#!/usr/bin/env python3
"""Генерирует index.html (RU) и en/index.html (EN) из одного шаблона.
Запуск: python3 build.py  — файлы появятся рядом со скриптом."""
import json, pathlib, re

SITE = "https://tm-g.xyz/"          # замените на свой домен (нужен для canonical/hreflang)
IMG = "/images/" 
RESUME = "https://drive.google.com/file/d/1NBAMx27IJ26ATKZMDvv_NGpCA-mL37s9/view?usp=drive_link"
CATS = ["marketing", "brand", "print", "web", "motion"]
DEFAULT_CAT = "marketing"

# ---- SEO и аналитика (пустая строка = функция отключена) ----
OG_IMAGE = "/images/og.jpg"       # картинка для превью ссылки, 1200x630. Положите файл в images/
FAVICON = "/favicon.svg"          # SVG-иконка в корне сайта (рекомендуют Яндекс и Google); пустая строка = не подключать
FAVICON_ICO = "/favicon.ico"      # запасная иконка .ico с размером 48x48 (Safari, старые браузеры); пустая строка = не подключать
APPLE_ICON = "/apple-touch-icon.png"   # PNG 180x180 для iPhone/iPad; пустая строка = не подключать
GTM_ID = ""                       # Google Tag Manager отключён. Прежний код: GTM-N57W9LLN; пустая строка = выключено
GTM_LANGS = ("ru", "en")          # на каких версиях подключать GTM. Только на английской: ("en",)
YANDEX_VERIFY = "c04398cf190402aa"                # код из метатега подтверждения Яндекс Вебмастера (если подтверждаете метатегом)
GOOGLE_VERIFY = "o49Ym7q_3oqd0ZwT0_iDKNUcBJTMZFgxB0_VBOsp4_c"                # код из метатега Google Search Console
METRIKA_CODE_SAVED = """<!-- Yandex.Metrika counter -->
<script type="text/javascript">
    (function(m,e,t,r,i,k,a){
        m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
        m[i].l=1*new Date();
        for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}
        k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
    })(window, document,'script','https://mc.yandex.ru/metrika/tag.js?id=114092503', 'ym');

    ym(114092503, 'init', {ssr:true, webvisor:true, clickmap:true, ecommerce:"dataLayer", referrer: document.referrer, url: location.href, accurateTrackBounce:true, trackLinks:true});
</script>
<noscript><div><img src="https://mc.yandex.ru/watch/114092503" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
<!-- /Yandex.Metrika counter -->"""                 # сюда целиком вставьте код счётчика Яндекс Метрики (с тегами <script> и <noscript>)
METRIKA_CODE = ""               # счётчик отключён. Чтобы включить снова: METRIKA_CODE = METRIKA_CODE_SAVED

DARK = "--bg:#0e1614;--surface:#15211e;--ink:#e6efec;--muted:#94a8a2;--line:#263631;--accent-text:#52a595;color-scheme:dark;"

T = {
 "ru": dict(lang="ru", path="", other="en/", other_label="EN", other_title="English version", home="./",
  title="Артём Гольфингер — графический дизайнер",
  desc="Дизайн, который работает одинаково эффективно в digital и офлайне: рекламные креативы, брендинг, соцсети, наружная реклама, полиграфия и сайты.",
  nav=["кейсы", "услуги", "контакты", "резюме ↗"], navlabel="Основная навигация", theme="Сменить тему",
  hi="Привет! Меня зовут Артём", h1="графический дизайнер",
  lead="Я создаю дизайн, который работает одинаково эффективно в digital и офлайне — от рекламных креативов, брендинга и соцсетей до наружной рекламы, полиграфии и сайтов.",
  tg="Написать в Telegram", resume="Резюме", portfolio="Портфолио", filters="Фильтр кейсов", all="Все кейсы",
  cats=dict(marketing="Маркетинговый дизайн", brand="Логотипы и брендинг", print="Полиграфия и наружка", web="Сайты и лендинги", motion="Моушн"),
  services_h="Чем занимаюсь",
  services=[("Брендинг", "Логотип, фирменный стиль, айдентика."), ("Digital-дизайн", "Веб-баннеры, соцсети, digital-креативы."),
            ("Сайты", "Лендинги на Tilda и Webflow."), ("Полиграфия", "Наружная реклама, флаеры, листовки и другие печатные материалы."),
            ("Моушн", "2D- и 3D-анимация, анимированные баннеры.")],
  contact_h="Есть задача? Сделаем из неё сильное визуальное решение",
  contact_p="Напишите мне в мессенджер или на почту — отвечу и обсудим детали.",
  copy="Скопировать", copied="Скопировано", fail="Не удалось",
  footer="ИП Гольфингер А. С. · ИНН 1108 0674 5223",
  labels=dict(goal="Цель", task="Задача", role="Моя роль", result="Результаты"), prev="← Назад", next="Дальше →", close="Закрыть"),
 "en": dict(lang="en", path="en/", other="../", other_label="RU", other_title="Русская версия", home="../",
  title="Artem Golfinger — Graphic Designer",
  desc="Design that works equally well in digital and offline: ad creatives, branding, social media, outdoor advertising, print and websites.",
  nav=["cases", "services", "contact", "resume ↗"], navlabel="Main navigation", theme="Toggle theme",
  hi="Hi! My name is Artem", h1="graphic designer",
  lead="I create design that works equally well in digital and offline — from ad creatives, branding and social media to outdoor advertising, print and websites.",
  tg="WhatsApp me", resume="Resume", portfolio="Portfolio", filters="Case filter", all="All cases",
  cats=dict(marketing="Marketing design", brand="Logos and branding", print="Print and outdoor", web="Websites and landing pages", motion="Motion"),
  services_h="What I do",
  services=[("Branding", "Logo, brand identity, visual system."), ("Digital design", "Web banners, social media, digital creatives."),
            ("Websites", "Landing pages on Tilda and Webflow."), ("Print", "Outdoor advertising, flyers, leaflets and other printed materials."),
            ("Motion", "2D and 3D animation, animated banners.")],
  contact_h="Got a task? Let's turn it into a strong visual solution",
  contact_p="Message me on Telegram or WhatsApp, or send an email — I'll reply and we'll discuss the details.",
  copy="Copy", copied="Copied", fail="Failed",
  footer="Artem Golfinger",
  labels=dict(goal="Goal", task="Task", role="My role", result="Results"), prev="← Previous", next="Next →", close="Close"),
}

T["ru"].update(person="Артём Гольфингер", job="Графический дизайнер", locale="ru_RU",
                msg_url="https://t.me/tm_glfngr", resume_url=RESUME)
T["en"].update(person="Artem Golfinger", job="Graphic Designer", locale="en_US",
                msg_url="https://api.whatsapp.com/send/?phone=381637003927&text&type=phone_number&app_absent=0",
                resume_url="https://drive.google.com/file/d/1Ez2k4Exnvs7BfbY3vz7-wkF6EomK1c9k/view?usp=sharing")

# Политика конфиденциальности в подвале. Вставьте свои адреса между кавычками.
# Пока адрес пустой, в подвале показывается обычный текст без ссылки.
PRIVACY = {
    "ru": ("Политика конфиденциальности", "https://drive.google.com/file/d/19d-4PYgY0I8k-LFAp5CZac5NbDu22chs/view?usp=sharing"),
    "en": ("Privacy Policy", "https://drive.google.com/file/d/13LqEZd1-0V4aeaVfQbFk30g9kjJeNb6z/view?usp=sharing"),
}

# Баннер согласия на cookie. Счётчики (Метрика, GTM) подключаются только после нажатия «Принять».
# {services} подставляется автоматически, {privacy} превращается в ссылку на политику.
CONSENT = {
    "ru": dict(
        text="Мы используем файлы cookie и сервисы аналитики ({services}), чтобы понимать, как посетители пользуются сайтом. "
             "Они включаются только с вашего согласия. Подробнее — в {privacy}.",
        privacy_inline="политике конфиденциальности", yes="Принять", no="Отклонить",
        settings="Настройки cookie", yandex="Яндекс Метрика"),
    "en": dict(
        text="We use cookies and analytics services ({services}) to understand how visitors use the site. "
             "They are enabled only with your consent. More details in the {privacy}.",
        privacy_inline="Privacy Policy", yes="Accept", no="Decline",
        settings="Cookie settings", yandex="Yandex Metrica"),
}

# ============================ КЕЙСЫ ============================
# Добавить кейс  — скопируйте любой блок dict(...) целиком и поменяйте поля.
# Удалить кейс   — удалите блок dict(...) целиком (вместе с запятой в конце).
# Порядок карточек на сайте = порядок блоков здесь.
# Убрать блок внутри кейса (Цель, Задача, Роль, Результат) — замените его текст на None.
# Добавить свой блок внутри кейса — ключи ru_extra / en_extra: [("Заголовок блока", "Текст")].
# c — категория, t — превью (карточка), i — большое изображение в окне кейса (если нет — берётся превью)
# кортеж: (заголовок, цель, задача, роль, результат)
CASES = [
 dict(c="marketing", t="01p.webp", i="01.webp",
  ru=("Веб-баннеры для Helix",
      "Дизайн рекламных креативов для маркетинговых активностей Helix: важна была не только визуальная часть, но и эффективность с точки зрения конверсии.",
      "Разрабатывать визуальные концепции для кампаний и акций и адаптировать их под разные каналы и форматы: РСЯ, геосервисы, соцсети и другие digital-размещения.",
      "Разрабатывал креативы от концепции до готовых макетов с учётом маркетинговых задач. Делал ресайзы и адаптации под форматы и площадки (РСЯ, ГЕО, СММ и др.).",
      "Креативы показывали высокую эффективность. В отдельных кампаниях CTR вырос с 0,1% <b>до 0,5%</b> (РСЯ). Финансовый результат одной из акций — +300% продаж от плана."),
  en=("Web banners for Helix",
      "Design ad creatives for Helix marketing activities, focusing not only on visual appeal but on campaign performance.",
      "Develop visual concepts for campaigns and promotions and adapt them to different channels and formats: Yandex Advertising Network, geo services, social media and other digital placements.",
      "Developed creatives from concept to final layouts, driven by marketing goals. Made resizes and adaptations for different formats and ad platforms.",
      "The creatives performed strongly. In some campaigns CTR grew from 0.1% <b>to 0.5%</b> (Yandex Advertising Network). One promotion delivered +300% sales against the plan.")),
 dict(c="marketing", t="02p.webp", i="02.webp",
  ru=("Другие баннеры и рекламные креативы",
      "Разработать эффективные рекламные креативы для бизнеса в разных нишах и под разные маркетинговые задачи.",
      "Создать баннеры и рекламные материалы для разных форматов и каналов с учётом целевой аудитории, задач кампании и требований площадки.",
      "Вёл проекты с заказчиками End-to-End. Консультировал по визуальной подаче и предлагал решения для повышения конверсии.",
      "Создано большое количество креативов для разных ниш и форматов. Выработан системный подход: визуальная привлекательность сочетается с понятной подачей предложения и маркетинговой эффективностью."),
  en=("Other banners and ad creatives",
      "Develop effective ad creatives for businesses in different niches and for different marketing goals.",
      "Create banners and advertising materials for various formats and channels, taking into account the target audience, campaign goals and platform requirements.",
      "Led projects with clients end to end: from discussing the task and developing several visual concepts to final layouts and adaptations. Advised on visual presentation and proposed solutions to improve conversion.",
      "Created a large number of creatives for different niches and formats. Built a systematic approach where visual appeal is combined with a clear offer and marketing effectiveness.")),
 dict(c="marketing", t="03p.webp", i="03.webp",
  ru=("Редизайн СММ Helix",
      "Обновить визуальный стиль соцсетей Helix: сделать его современнее и заметнее на фоне конкурентов, сохранив узнаваемость бренда и доверие аудитории.",
      "Разработать новое визуальное направление, которое отвечает актуальным трендам, привлекает новую аудиторию и остаётся понятным для текущей.",
      "Работал в кроссфункциональной команде с другим дизайнером и SMM-специалистами. Вместе с коллегой разработал несколько концепций, защищал их перед командой и после выбора направления участвовал в реализации.",
      "Создана обновлённая визуальная система соцсетей, которая сохранила узнаваемость бренда и стала современнее."),
  en=("Helix social media redesign",
      "Refresh the visual style of Helix social media: make it more modern and noticeable among competitors while keeping brand recognition and the trust of the existing audience.",
      "Develop a new visual direction that follows current design trends, attracts a new audience and stays clear and comfortable for the current one.",
      "Worked in a cross-functional team with another designer and SMM specialists. Together with my colleague I developed several concepts, defended them in front of the team and took part in implementing the chosen direction.",
      "Created an updated visual system for social media that kept the brand recognizable and made it more modern.")),
 dict(c="brand", t="04p.webp", i="04.webp",
  ru=("Редизайн логотипа Smiletogo",
      "Обновить визуальный образ сервиса Smiletogo и повысить узнаваемость бренда.",
      "Сделать редизайн логотипа и на его основе создать базу фирменного стиля: цвета, типографику, паттерн и шаблоны для соцсетей.",
      "Работал с заказчиком End-to-End: разработал несколько концепций логотипа и финализировал выбранную. Создал базовые элементы фирменного стиля и шаблоны для соцсетей.",
      "За 4 месяца после внедрения: конверсия сайта выросла на 12%, количество подписчиков — на 18%, вовлечённость в соцсетях — на 15%."),
  en=("Smiletogo logo redesign",
      "Refresh the visual image of the Smiletogo service and increase brand recognition.",
      "Redesign the logo and, based on it, create the foundation of the brand identity: colors, typography, pattern and social media templates.",
      "Worked with the client end to end: developed several logo concepts and finalized the chosen one. Created the core brand identity elements and social media templates.",
      "In 4 months after launch: website conversion grew by 12%, followers by 18%, and social media engagement by 15%.")),
 dict(c="brand", t="05p.webp", i="05.webp",
  ru=("Брендинг Go Каяк",
      "Создать узнаваемый фирменный стиль для сервиса аренды каяков: выделить бренд среди конкурентов и передать ощущение отдыха на природе, надёжности и профессионализма.",
      "Проанализировать аудиторию и конкурентов, определить визуальное направление и разработать айдентику, которая сочетает тематику воды и природы с современным образом.",
      "Провёл анализ аудитории и конкурентов, разработал концепцию и фирменный стиль: логотип, палитру, типографику и паттерн. Продумал систему визуальных элементов и правила их использования.",
      "Цельная айдентика, объединяющая природу и воду с образом надёжного сервиса. Все элементы систематизированы в едином гайдбуке."),
  en=("Go Kayak branding",
      "Create a recognizable brand identity for a kayak rental service that stands out from competitors and conveys outdoor leisure, reliability and professional support.",
      "Analyze the audience and competitors, define the visual direction and develop an identity that combines water and nature themes with a modern, professional brand image.",
      "Analyzed the audience and competitors, developed the concept and brand identity: logo, color palette, typography and pattern. Designed the system of visual elements and rules for using them.",
      "A cohesive identity that links nature and water with the image of a reliable service. All brand elements are organized in a single guidebook.")),
 dict(c="brand", t="06p.webp", i="06.webp",
  ru=("Брендинг Дог Пикник", "Заказчику необходима айдентика для проекта. В дизайне нужно было использовать цвета, которые ассоциируются с природой (трава, земля), а также сделать его дружелюбным (пёсики, всё такое). Был предоставлен мудборд.", "Я разработал логотип, подобрал цветовую палитру бренда и выбрал пару гармонирующих друг с другом шрифтов. Кроме того, я подготовил руководство по использованию визуального стиля и создал шаблоны для социальных сетей.", None, None), en=("Dog Picnic branding", "The client needed a visual identity for the project. The design had to use colors associated with nature, such as grass and earth tones, while creating a friendly and welcoming feel through elements like dogs and playful visuals. A moodboard was provided as a reference.", "I developed a logo, selected the brand color palette, and chose a pair of complementary fonts. I also provided guidelines for using the visual identity and created social media templates.", None, None)),
 dict(c="print", t="07p.webp", i="07.webp",
  ru=("Наружная реклама",
      "Дизайн макетов для наружных размещений, которые остаются заметными и легко считываются в условиях города.",
      "Разработать дизайн для крупноформатных баннеров 3×6 м и digital-экранов с анимацией 5–15 секунд с учётом технических требований каждого формата.",
      "Полностью выполнял дизайн макетов: учитывал техтребования, дистанцию просмотра, читаемость деталей, освещённость, погоду и особенности размещения. Для digital-экранов проработал короткие анимации и адаптации.",
      "Макеты размещались на наружных конструкциях и digital-экранах в людных местах Санкт-Петербурга, Москвы, Новосибирска, Махачкалы и других крупных городов."),
  en=("Outdoor advertising",
      "Design layouts for outdoor placements that stay eye-catching and easy to read in real urban conditions.",
      "Develop designs for large-format 3×6 m billboards and digital screens with 5–15 second animations, following the technical requirements of each format.",
      "Handled the full layout design: accounted for technical requirements, viewing distance, legibility of details, lighting, weather and placement specifics. For digital screens I also developed short animations and adaptations.",
      "The layouts were placed on outdoor structures and digital screens in busy locations in St. Petersburg, Moscow, Novosibirsk, Makhachkala and other large cities.")),
dict(c="print", t="08p.webp", i="08.webp",
  ru=("Постер к саммиту Traffic Summit", "", "", "", ""),
  en=("Traffic Summit Poster", "", "", "", "")), 
dict(c="print", t="09p.webp", i="09.webp",
  ru=("Полиграфия", None, None, None, None), en=("Print design", None, None, None, None)),
 dict(c="web", t="10p.webp", i="10.webp",
  ru=("Спецпроект-игра Helix",
      "Создать интерактивный спецпроект, который в вовлекающей форме знакомит клиентов Helix с продуктами и услугами компании.",
      "Разработать концепцию лендинга с элементами геймификации, сочетающую развлечение и нативное продвижение продуктов, акций и спецпредложений.",
      "Предложил концепцию и вместе с командой дизайнеров и маркетологов доработал её. Отвечал за визуальную часть, игровые механики, сценарии взаимодействия и UX.",
      "Интерактивный квест, который с юмором знакомит с продуктами и услугами Helix, вовлекает в игру и нативно предлагает акции и скидки."),
  en=("Helix game special project",
      "Create an interactive special project that introduces Helix customers to the company's products and services in an engaging way.",
      "Develop a landing page concept with gamification elements that combines entertainment with native promotion of products, offers and discounts.",
      "Proposed the concept and refined it together with a team of designers and marketers. Responsible for the visual part, game mechanics, interaction scenarios and user experience.",
      "An interactive quest that introduces Helix products and services with humor, draws users into the game and offers promotions and discounts natively.")),
 dict(c="web", t="11p.webp", i="11.webp",
  ru=("Дизайн сервисных рассылок",
      "Унифицировать сервисные рассылки и сделать коммуникацию понятнее, современнее и узнаваемее.",
      "Привести в порядок макеты транзакционных писем: регистрация, смена пароля, накопление баллов, действия в личном кабинете, программа лояльности и другие.",
      "Провёл редизайн и унифицировал визуальную систему рассылок, улучшил структуру и читаемость. Адаптировал макеты под разные устройства и форматы.",
      "Единая система сервисных коммуникаций: удобнее для пользователей, лучше соответствует стилю бренда и узнаваема во всех типах писем."),
  en=("Service email design",
      "Unify service emails and make communication clearer, more modern and more recognizable for users.",
      "Bring order to transactional email layouts: registration, password reset, loyalty points, account actions, loyalty program and other service messages.",
      "Redesigned and unified the visual system of the emails, improved structure and readability. Adapted the layouts to different devices and display formats.",
      "A single system of service communications that is easier for users, matches the brand style better and is recognizable across all email types.")),
 dict(c="web", t="12p.webp", i="12.webp",
  ru=("Лендинг для интерактивного музея",
      "Создать современный атмосферный лендинг для запуска интерактивного музея сказок Readles в Дубае.",
      "Разработать визуальную концепцию, которая сочетает сказочную тематику с атмосферой технологий будущего и AI и понятно показывает интерактивный формат музея.",
      "Спроектировал дизайн лендинга: концепцию и композицию, решения для технологичной атмосферы, интерактивные блоки и адаптивные версии.",
      "Цельный лендинг, объединяющий сказку, технологии будущего и AI. Концепция передаёт инновационный характер музея."),
  en=("Landing page for an interactive museum",
      "Create a modern, atmospheric landing page for the launch of Readles, an interactive fairy-tale museum in Dubai.",
      "Develop a visual concept that blends a fairy-tale theme with the atmosphere of future technology and AI, while clearly presenting the museum's interactive format.",
      "Designed the landing page: developed the concept and visual composition, chose solutions to convey a high-tech atmosphere, designed interactive blocks and prepared responsive versions.",
      "A cohesive landing page that combines fairy tales, future technology and AI. The visual concept conveys the museum's innovative character.")),
 dict(c="web", t="13p.webp", i="13.webp",
  ru=("Редизайн сайта PRO-сервис",
      "Повысить эффективность сайта бизнес-коуча, улучшить пользовательский путь и увеличить конверсию.",
      "Провести аудит сайта на Tilda, найти слабые места в структуре, воронке, конверсии и SEO и определить, как улучшить UX.",
      "Провёл аудит и предложил улучшения структуры и визуальной подачи. Реализовал редизайн на Tilda: формы, оплата, доставка, CRM, адаптивные версии.",
      "Обновлены структура и визуальная подача, устранены выявленные проблемы, улучшен пользовательский путь — конверсия сайта выросла."),
  en=("PRO-service website redesign",
      "Make a business coach's website more effective, improve the user journey and increase conversion.",
      "Audit the existing Tilda website, identify weak points in structure, funnel, conversion and SEO, and find ways to improve the user experience.",
      "Audited the site and proposed improvements to structure and visual presentation. Implemented the redesign on Tilda, including forms, payment, delivery, CRM and responsive versions.",
      "Updated the structure and visual presentation, fixed the identified issues and improved the user journey, which increased the website's conversion.")),

 # ---- MOTION: заглушки. Замените названия, тексты, превью (t) и видео (i) на свои ----
 dict(c="motion", t="/images/14p.webp", i="/videos/motion-1.mp4",
  ru=("Анимированные баннеры для Olymptrade", "Создать современные анимированные рекламные баннеры для продвижения fintech-продукта и привлечения внимания потенциальных пользователей.", "Разработать минималистичные горизонтальные баннеры с акцентом на ключевые преимущества продукта. Продумать плавную анимацию и CTA-элементы, используя современные motion-эффекты без визуальной перегруженности.", "", "Созданы лаконичные анимированные баннеры продолжительностью 5–10 секунд в современном fintech-стиле."),
  en=("Animated advertising banners for Olymptrade", "Create modern animated advertising banners to promote a fintech product and attract potential users.", "Design minimalist horizontal banners highlighting the product's key benefits. Develop smooth animations and CTA elements, using modern motion effects without making the visuals feel cluttered.", "", "Created clean, minimalist animated banners in a modern fintech style, with a duration of 5–10 seconds."),
  ru_extra=[("Инструменты", "After Effects")], en_extra=[("Tools", "After Effects")]),
 dict(c="motion", t="/images/15p.webp", i="/videos/motion-2.mp4",
  ru=("Баннер для virtualcards", "Повысить эффективность рекламы виртуальных карт за счёт создания яркого и заметного анимационного баннера, способного выделиться среди конкурентов и привлечь внимание аудитории.", "Проанализировать рекламные креативы конкурентов, определить эффективные визуальные приёмы и разработать собственную концепцию баннера. Создать статичный макет и дополнить его простой, но выразительной анимацией.", "", "Создан анимационный рекламный баннер с акцентом на визуальную заметность, понятную подачу предложения и привлечение внимания потенциальных клиентов."),
  en=("Banner for virtualcards", "Improve the performance of virtual card advertising by creating a bold, eye-catching animated banner that stands out from competitors and attracts the target audience.", "Analyze competitors' advertising creatives, identify effective visual techniques, and develop a unique banner concept. Create a static design and bring it to life with simple yet engaging animation.", "", "Created an animated advertising banner focused on visual impact, clear messaging, and attracting the attention of potential customers."),
  ru_extra=[("Инструменты", "After Effects, Blender")], en_extra=[("Tools", "After Effects, Blender")]),
]

TEMPLATE = r"""<!DOCTYPE html>
<html lang="[[lang]]">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>[[title]]</title>
<meta name="description" content="[[desc]]">
<link rel="canonical" href="[[site]][[path]]">
<link rel="alternate" hreflang="ru" href="[[site]]">
<link rel="alternate" hreflang="en" href="[[site]]en/">
<link rel="alternate" hreflang="x-default" href="[[site]]">
[[seo]]
[[fonts_head]]
<script>try{var t=localStorage.getItem("theme");if(t)document.documentElement.dataset.theme=t}catch(e){}</script>
<style>
[[fonts_css]]
:root{
  --bg:#f2f6f5;--surface:#fff;--ink:#12201d;--muted:#55655f;--line:#cfdcd8;
  --accent:#2a7064;--accent-text:#2a7064;--on-accent:#fff;
  --radius:20px;--pad:clamp(20px,4vw,56px);
  --head:"PT Sans",system-ui,sans-serif;--body:"Inter",system-ui,sans-serif;color-scheme:light;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){[[dark]]}}
:root[data-theme="dark"]{[[dark]]}
*,*::before,*::after{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:84px}
body{margin:0;background:var(--bg);color:var(--ink);font:400 17px/1.6 var(--body);-webkit-font-smoothing:antialiased}
img{display:block;max-width:100%}
a{color:inherit}
h1,h2,h3{font-family:var(--head);font-weight:700;margin:0;text-wrap:balance}
p,dd,li{text-wrap:pretty}
:focus-visible{outline:3px solid var(--accent-text);outline-offset:3px;border-radius:6px}
.wrap{max-width:1280px;margin:0 auto;padding:0 var(--pad)}
.btn{display:inline-flex;align-items:center;gap:.5em;padding:.85em 1.5em;border-radius:999px;border:1.5px solid var(--accent);background:none;color:var(--accent-text);font:400 16px var(--body);text-decoration:none;cursor:pointer;transition:background .2s,color .2s}
.btn:hover{background:var(--accent);color:var(--on-accent)}
.btn.primary{background:var(--accent);color:var(--on-accent)}
.btn.primary:hover{filter:brightness(1.15)}

header{position:sticky;top:0;z-index:10;background:color-mix(in srgb,var(--bg) 90%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
header .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:68px}
.logo{font:700 20px var(--head);text-decoration:none;color:var(--accent-text)}
nav{display:flex;gap:clamp(16px,3vw,32px)}
nav a{padding:6px 0;border-bottom:2px solid transparent;text-decoration:none;font-size:15px;color:var(--muted);transition:color .2s,border-color .2s}
nav a:hover{color:var(--ink)}
nav a[aria-current="true"]{color:var(--accent-text);border-color:var(--accent)}
.tools{display:flex;gap:8px}
.tools a,.tools button{display:grid;place-items:center;min-width:40px;height:40px;padding:0 10px;border:1.5px solid var(--accent);border-radius:999px;background:none;color:var(--accent-text);font:400 14px var(--body);text-decoration:none;cursor:pointer;transition:background .2s,color .2s}
.tools a:hover,.tools button:hover{background:var(--accent);color:var(--on-accent)}
.tools svg{width:18px;height:18px}
@media(max-width:560px){
  html{scroll-padding-top:120px}
  header .wrap{flex-wrap:wrap;padding-block:8px}
  nav{order:3;width:100%;justify-content:space-between}
  nav a:last-child{display:none}
}

.hero{padding-block:clamp(40px,10vw,128px) clamp(40px,6vw,72px)}
.hi{margin:0 0 20px;color:var(--muted)}
.wave{display:inline-block;transform-origin:70% 70%;animation:wave 2.2s ease-in-out .5s infinite}
@keyframes wave{0%,60%,100%{transform:rotate(0)}10%{transform:rotate(14deg)}20%{transform:rotate(-8deg)}30%{transform:rotate(14deg)}40%{transform:rotate(-4deg)}50%{transform:rotate(10deg)}}
h1{font-size:clamp(44px,9vw,120px);line-height:1;letter-spacing:-.01em;max-width:12ch;color:var(--accent-text)}
@media(min-width:900px){
  .hero{padding-top:clamp(24px,6vh,96px)}
  h1{font-size:clamp(44px,min(9vw,14vh),120px)}
}
.lead{max-width:56ch;margin:32px 0;font-size:clamp(17px,1.6vw,20px);color:var(--muted)}
.actions{display:flex;flex-wrap:wrap;gap:12px}
.ticker{overflow:hidden;border-block:1px solid var(--line);padding:16px 0;margin-top:clamp(40px,6vw,72px)}
.ticker-track{display:flex;gap:40px;width:max-content;animation:tick 40s linear infinite;font-size:clamp(18px,2vw,24px);color:var(--muted)}
@keyframes tick{to{transform:translateX(-50%)}}

section{padding:clamp(56px,8vw,112px) 0}
h2{margin-bottom:32px;font-size:clamp(32px,4.4vw,56px);line-height:1.1;color:var(--accent-text)}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:32px}
.chip{padding:.55em 1.1em;border-radius:999px;border:1.5px solid var(--accent);background:none;color:var(--accent-text);font:400 15px var(--body);cursor:pointer;transition:background .2s,color .2s}
.chip:hover{background:color-mix(in srgb,var(--accent) 16%,transparent)}
.chip[aria-pressed="true"]{background:var(--accent);color:var(--on-accent)}
@media(max-width:700px){
  .filters{flex-wrap:nowrap;overflow-x:auto;margin-inline:calc(var(--pad)*-1);padding:2px var(--pad);scroll-snap-type:x proximity;scrollbar-width:none;-webkit-overflow-scrolling:touch}
  .filters::-webkit-scrollbar{display:none}
  .chip{flex:none;white-space:nowrap;scroll-snap-align:center}
}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,360px),1fr));gap:28px 24px}
.card{display:flex;flex-direction:column;gap:12px;padding:0;border:0;background:none;color:inherit;text-align:left;font:inherit;cursor:pointer}
.card[hidden]{display:none}
.thumb{aspect-ratio:4/3;overflow:hidden;border-radius:var(--radius);background:var(--surface)}
.card img{width:100%;height:100%;object-fit:cover;transition:transform .5s cubic-bezier(.2,.7,.2,1)}
.card:hover img{transform:scale(1.04)}
.card h3{font-size:22px;line-height:1.25}

.services{list-style:none;margin:0;padding:0;border-top:1px solid var(--line)}
.services li{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.2fr);gap:12px 40px;padding:28px 0;border-bottom:1px solid var(--line)}
.services h3{font-size:clamp(24px,3vw,36px);line-height:1.15}
.services p{margin:0;color:var(--muted)}
@media(max-width:700px){.services li{grid-template-columns:1fr}}

.contact{background:var(--accent);color:#fff;border-radius:calc(var(--radius)*1.6);padding:clamp(32px,6vw,80px)}
.contact h2{max-width:18ch;color:#fff}
.contact p{max-width:48ch;margin:0 0 32px;color:rgb(255 255 255/.8)}
.contact .btn{border-color:#fff;color:#fff}
.contact .btn:hover{background:#fff;color:var(--accent)}
.contact .btn.primary{background:#fff;color:var(--accent)}
.mail{display:flex;align-items:center;gap:12px;margin-top:28px;flex-wrap:wrap}
.mail a{font-size:clamp(18px,2.4vw,26px);text-decoration:none}
.copy{padding:.5em 1em;font-size:14px}
footer{padding:40px 0 56px;color:var(--muted);font-size:14px}
footer .wrap{display:flex;flex-wrap:wrap;justify-content:space-between;gap:16px}
footer p{margin:0}
footer a{color:inherit;text-underline-offset:3px}
.linkbtn{padding:0;border:0;background:none;font:inherit;color:inherit;text-decoration:underline;text-underline-offset:3px;cursor:pointer}
.consent{position:fixed;left:16px;right:16px;bottom:16px;z-index:30;max-width:760px;display:flex;align-items:center;gap:16px 24px;padding:16px 20px;border:1px solid var(--line);border-radius:var(--radius);background:var(--surface);box-shadow:0 12px 40px rgb(0 0 0/.18);animation:pop .28s cubic-bezier(.2,.7,.2,1)}
.consent[hidden]{display:none}
.consent p{margin:0;font-size:14px;line-height:1.5;color:var(--muted)}
.consent a{color:var(--accent-text)}
.consent-actions{display:flex;gap:8px;flex:none}
.consent .btn{padding:.6em 1.1em;font-size:14px}
@media(max-width:640px){.consent{flex-direction:column;align-items:stretch}.consent-actions .btn{flex:1;justify-content:center}}

/* окно кейса: левая колонка 380px + изображение на всю высоту. При ширине окна 1100px и высоте 720px изображение — квадрат 720×720 */
dialog{width:min(1100px,calc(100% - 32px));height:min(720px,calc(100dvh - 32px));max-height:none;padding:0;border:0;border-radius:var(--radius);background:var(--surface);color:var(--ink);overflow:hidden}
dialog::backdrop{background:rgb(6 12 10/.7);backdrop-filter:blur(4px)}
dialog[open]{display:grid;grid-template-columns:380px minmax(0,1fr);animation:pop .28s cubic-bezier(.2,.7,.2,1)}
@keyframes pop{from{opacity:0;transform:translateY(16px) scale(.98)}}
.m-info{display:flex;flex-direction:column;gap:20px;padding:36px 32px;overflow-y:auto}
.m-info h2{margin:0;font-size:28px;line-height:1.15}
.m-info dl{display:grid;gap:18px;margin:0}
.m-info dt{margin:0 0 4px;font:700 17px var(--head);color:var(--accent-text)}
.m-info dd{margin:0;font-size:14px;line-height:1.15}
.m-nav{display:flex;gap:8px;margin-top:auto;padding-top:8px}
.m-nav .btn{padding:.6em 1.1em;font-size:14px}
.m-media{position:relative;overflow:hidden;isolation:isolate;border-radius:0 var(--radius) var(--radius) 0;background:var(--bg)}
.m-media img,.m-media video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.m-media [hidden]{display:none}
.m-media img{transition:opacity .2s}
.m-media img.is-loading{opacity:0}
.m-media video{cursor:pointer}
.close{position:absolute;top:12px;right:12px;z-index:2;width:44px;height:44px;border-radius:50%;border:0;background:var(--accent);color:#fff;font-size:24px;line-height:1;cursor:pointer}
@media(max-width:800px){
  dialog[open]{display:flex;flex-direction:column;height:auto;max-height:calc(100dvh - 32px);overflow-y:auto}
  .m-media{order:-1;flex:none;aspect-ratio:1/1;border-radius:var(--radius) var(--radius) 0 0}
  .m-info{overflow:visible;padding:24px 20px}
}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
</style>
[[analytics]]
</head>
<body>
[[body_start]]

<header>
  <div class="wrap">
    <a class="logo" href="#top">tm.glfngr</a>
    <nav aria-label="[[navlabel]]">
      <a href="#cases">[[nav0]]</a>
      <a href="#services">[[nav1]]</a>
      <a href="#contact">[[nav2]]</a>
      <a href="[[resume_url]]" target="_blank" rel="noopener">[[nav3]]</a>
    </nav>
    <div class="tools">
      <a href="[[other]]" hreflang="[[other_label_lc]]" lang="[[other_label_lc]]" title="[[other_title]]">[[other_label]]</a>
      <button type="button" id="theme" aria-label="[[theme]]" title="[[theme]]"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor"/></svg></button>
    </div>
  </div>
</header>

<main id="top">
  <div class="hero wrap" id="hero">
    <p class="hi"><span class="wave" aria-hidden="true">👋</span> [[hi]]</p>
    <h1>[[h1]]</h1>
    <p class="lead">[[lead]]</p>
    <div class="actions">
      <a class="btn primary" href="[[msg_url]]" target="_blank" rel="noopener">[[tg]]</a>
      <a class="btn" href="[[resume_url]]" target="_blank" rel="noopener">[[resume]]</a>
    </div>
  </div>
  <div class="ticker" aria-hidden="true"><div class="ticker-track" id="ticker"></div></div>

  <section id="cases">
    <div class="wrap">
      <h2>[[portfolio]]</h2>
      <div class="filters" role="group" aria-label="[[filters_label]]" id="filters">[[chips]]</div>
      <div class="grid" id="grid">[[cards]]</div>
    </div>
  </section>

  <section id="services">
    <div class="wrap">
      <h2>[[services_h]]</h2>
      <ul class="services">[[services]]</ul>
    </div>
  </section>

  <section id="contact">
    <div class="wrap">
      <div class="contact">
        <h2>[[contact_h]]</h2>
        <p>[[contact_p]]</p>
        <div class="actions">
          <a class="btn primary" href="https://t.me/tm_glfngr" target="_blank" rel="noopener">Telegram</a>
          <a class="btn" href="https://wa.me/381637003927" target="_blank" rel="noopener">WhatsApp</a>
        </div>
        <div class="mail">
          <a href="mailto:artem.golfinger@gmail.com">artem.golfinger@gmail.com</a>
          <button class="btn copy" type="button" id="copy">[[copy]]</button>
        </div>
      </div>
    </div>
  </section>
</main>

<footer><div class="wrap"><div class="foot"><p>[[footer]]</p><p>[[privacy]][[cookie_link]]</p></div><span>© 2026</span></div></footer>

<dialog id="modal" aria-labelledby="m-title">
  <button class="close" type="button" aria-label="[[close]]" id="m-close">×</button>
  <div class="m-info">
    <h2 id="m-title"></h2>
    <dl id="m-body"></dl>
    <div class="m-nav">
      <button class="btn" type="button" id="m-prev">[[prev]]</button>
      <button class="btn" type="button" id="m-next">[[next]]</button>
    </div>
  </div>
  <div class="m-media"><img id="m-img" alt=""><video id="m-video" muted loop playsinline preload="metadata" hidden></video></div>
</dialog>

[[consent_html]]

<script>
const CASES = [[cases_json]];
const LABELS = [[labels_json]];
const TXT = {copy:"[[copy]]", copied:"[[copied]]", fail:"[[fail]]"};
const $ = id => document.getElementById(id);
const grid = $("grid"), modal = $("modal");
let visible = [], current = 0;

// бегущая строка
const tags = ["3D","web design","digital","animation","brand identity","landing","ux/ui","motion","ai","smm","print","illustration","presentation","tilda","marketing"];
$("ticker").innerHTML = [...tags, ...tags].map(t => `<span>${t}</span>`).join("");

// фильтры
const filters = $("filters");
filters.addEventListener("click", e => {
  const b = e.target.closest(".chip"); if (!b) return;
  const key = b.dataset.key;
  b.scrollIntoView({inline:"center", block:"nearest", behavior:"smooth"});
  filters.querySelectorAll(".chip").forEach(c => c.setAttribute("aria-pressed", c === b));
  grid.querySelectorAll(".card").forEach(c => c.hidden = key !== "all" && c.dataset.cat !== key);
});

// окно кейса
const vid = $("m-video"), pic = $("m-img");
const calm = matchMedia("(prefers-reduced-motion: reduce)").matches;
function stopVideo(){ vid.pause(); vid.removeAttribute("src"); vid.load(); }
let mediaToken = 0;
const preload = i => { const c = CASES[i]; if (c && !c.video) new Image().src = c.img; };
function showMedia(c){
  const token = ++mediaToken;                  // защита от быстрого листания: применяем только последний запрос
  stopVideo();                                 // старое видео и его последний кадр убираем сразу
  if (c.video) {
    pic.hidden = true; pic.removeAttribute("src");
    vid.hidden = false; vid.poster = c.poster; vid.src = c.img; vid.setAttribute("aria-label", c.title);
    vid.controls = calm;                       // при «уменьшить анимацию» автозапуска нет, показываем кнопки
    if (!calm) vid.play().catch(() => {});
  } else {
    vid.hidden = true; vid.removeAttribute("poster");
    pic.hidden = false; pic.alt = c.title;
    pic.removeAttribute("src"); pic.classList.add("is-loading");   // предыдущее изображение пропадает сразу
    const next = new Image();
    const done = () => { if (token !== mediaToken) return; pic.src = c.img; pic.classList.remove("is-loading"); };
    next.onload = done; next.onerror = done;
    next.src = c.img;                          // новое показываем, когда оно загружено
  }
}
vid.addEventListener("click", () => { if (!calm) vid.paused ? vid.play() : vid.pause(); });
function render(i){
  const c = CASES[i];
  $("m-title").textContent = c.title;
  const rows = Object.keys(LABELS).filter(k => c[k]).map(k => [LABELS[k], c[k]]).concat(c.extra || []);
  $("m-body").innerHTML = rows.map(([l, v]) => `<div><dt>${l}</dt><dd>${v}</dd></div>`).join("");
  showMedia(c);
  if (visible.length > 1) [visible[(current + 1) % visible.length], visible[(current - 1 + visible.length) % visible.length]].forEach(preload);
  modal.querySelector(".m-info").scrollTop = 0;
}
function openCase(i){
  visible = [...grid.querySelectorAll(".card:not([hidden])")].map(c => +c.dataset.i);
  current = visible.indexOf(i);
  render(i);
  if (!modal.open) modal.showModal();
  document.documentElement.style.overflow = "hidden";
}
function step(d){ current = (current + d + visible.length) % visible.length; render(visible[current]); }
grid.addEventListener("click", e => { const c = e.target.closest(".card"); if (c) openCase(+c.dataset.i); });
$("m-prev").onclick = () => step(-1);
$("m-next").onclick = () => step(1);
$("m-close").onclick = () => modal.close();
modal.addEventListener("click", e => { if (e.target === modal) modal.close(); });
modal.addEventListener("close", () => { document.documentElement.style.overflow = ""; stopVideo(); });
modal.addEventListener("keydown", e => { if (e.key === "ArrowLeft") step(-1); if (e.key === "ArrowRight") step(1); });

// подсветка текущего раздела в меню
const links = [...document.querySelectorAll("nav a[href^='#']")];
function mark(id){
  links.forEach(a => {
    if (a.getAttribute("href") === "#" + id) a.setAttribute("aria-current", "true");
    else a.removeAttribute("aria-current");
  });
}
const spy = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) mark(e.target.id); }), {rootMargin:"-40% 0px -55% 0px"});
["hero","cases","services","contact"].forEach(id => spy.observe($(id)));
addEventListener("scroll", () => { if (innerHeight + scrollY >= document.body.scrollHeight - 4) mark("contact"); }, {passive:true});

// тема: по умолчанию системная, выбор пользователя запоминается
$("theme").onclick = () => {
  const root = document.documentElement;
  const dark = root.dataset.theme ? root.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
  root.dataset.theme = dark ? "light" : "dark";
  try { localStorage.setItem("theme", root.dataset.theme); } catch (e) {}
};

// согласие на cookie: счётчики подключаются только после «Принять»
const ANALYTICS = [[analytics_json]];
const consentBox = $("consent");
const getConsent = () => { try { return localStorage.getItem("consent"); } catch (e) { return null; } };
const setConsent = v => { try { localStorage.setItem("consent", v); } catch (e) {} };
let analyticsOn = false;
function loadAnalytics(){
  if (analyticsOn || !ANALYTICS) return;
  analyticsOn = true;
  const tpl = document.createElement("template");
  tpl.innerHTML = ANALYTICS;
  tpl.content.querySelectorAll("script").forEach(old => {
    const s = document.createElement("script");
    Array.from(old.attributes).forEach(a => s.setAttribute(a.name, a.value));
    s.text = old.textContent;
    document.head.appendChild(s);
  });
}
function clearAnalyticsCookies(){
  const host = location.hostname, parts = host.split(".");
  const domains = [host, "." + host];
  for (let i = 1; i < parts.length - 1; i++) domains.push("." + parts.slice(i).join("."));
  const names = document.cookie.split(";").map(c => c.split("=")[0].trim()).filter(n => /^(_ym|_ga|_gid|_gat|_gcl)/.test(n));
  names.forEach(n => {
    domains.forEach(d => { document.cookie = n + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; domain=" + d; });
    document.cookie = n + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/";
  });
}
if (consentBox) {
  const saved = getConsent();
  if (saved === "granted") loadAnalytics(); else if (!saved) consentBox.hidden = false;
  $("consent-yes").onclick = () => { setConsent("granted"); consentBox.hidden = true; loadAnalytics(); };
  $("consent-no").onclick = () => { const was = analyticsOn; setConsent("denied"); consentBox.hidden = true; clearAnalyticsCookies(); if (was) location.reload(); };
  $("cookie-settings").onclick = () => { consentBox.hidden = false; $("consent-yes").focus(); };
}

// копирование почты
$("copy").onclick = async e => {
  const b = e.currentTarget;
  try { await navigator.clipboard.writeText("artem.golfinger@gmail.com"); b.textContent = TXT.copied; }
  catch { b.textContent = TXT.fail; }
  setTimeout(() => b.textContent = TXT.copy, 1800);
};
</script>
</body>
</html>
"""

HOME = "./"   # префикс до корня сайта для текущей страницы: "./" для RU, "../" для EN (выставляется в build)

def url(f):
    """Имя файла -> адрес. Полные адреса (https://...) не трогаем.
    Пути от корня (/images/..., /videos/...) превращаем в относительные (./images/... или ../images/...),
    чтобы сайт работал и на сервере, и при открытии файла двойным кликом с компьютера."""
    if not f.startswith("/"):
        f = IMG + f
    if f.startswith("/") and not f.startswith("//"):
        return HOME + f.lstrip("/")
    return f

VIDEO_EXT = (".mp4", ".webm", ".m4v")

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---- Типографика: неразрывные пробелы, чтобы не оставались «висячие» предлоги ----
NBSP = "\u00a0"
# Короткие слова, после которых пробел становится неразрывным. Нужное слово можно дописать через |
SHORT_WORDS = ("в|во|к|ко|с|со|у|о|об|и|а|я|но|на|по|за|от|до|из|не|ни|же|ли|бы|для|без|при|про|над|под|или"
               "|a|an|in|on|to|of|at|by|or|as")
_re_short = re.compile(r"(?<![\w\-])(" + SHORT_WORDS + r")\s+", re.I)
_re_dash = re.compile(r"\s+—")                                    # пробел перед тире
_re_init = re.compile(r"\b([А-ЯЁA-Z])\.\s+(?=[А-ЯЁA-Z])")             # инициалы: А. С. Гольфингер
_re_unit = re.compile(r"(\d)\s+(?=(?:мм|см|км|кг|м|сек|мин|ГБ|МБ|КБ|₽|%)(?!\w))")  # число + единица
_re_grp = re.compile(r"(?<=\d{4})\s(?=\d{4})")                    # 1108 0674 5223

def nb(s):
    """Расставляет неразрывные пробелы в тексте. Теги (<b>) не затрагиваются."""
    if not s: return s
    s = _re_short.sub(lambda m: m.group(1) + NBSP, s)
    s = _re_dash.sub(NBSP + "—", s)
    s = _re_init.sub(lambda m: m.group(1) + "." + NBSP, s)
    s = _re_unit.sub(lambda m: m.group(1) + NBSP, s)
    return _re_grp.sub(NBSP, s)


GOOGLE_FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
                '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
                '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400&family=PT+Sans:wght@700&display=swap" rel="stylesheet">')

def font_blocks(l):
    """Шрифты с вашего сервера, если есть fonts/fonts.json (создаётся скриптом get_fonts.py).
    Пока папки нет, временно подключаются Google Fonts, чтобы сайт не остался без шрифтов."""
    manifest = pathlib.Path(__file__).parent / "fonts" / "fonts.json"
    if not manifest.exists():
        print("Внимание: папка fonts/ не найдена, пока используются Google Fonts. Запустите: python3 get_fonts.py")
        return GOOGLE_FONTS, ""
    main = "cyrillic" if l == "ru" else "latin"     # основной набор символов страницы грузится заранее
    css, pre = [], []
    for it in json.loads(manifest.read_text(encoding="utf-8")):
        src = HOME + "fonts/" + it["file"]
        css.append(f'@font-face{{font-family:"{it["family"]}";font-style:normal;font-weight:{it["weight"]};'
                   f'font-display:swap;src:url({src}) format("woff2");unicode-range:{it["range"]}}}')
        if it["subset"] == main:
            pre.append(f'<link rel="preload" href="{src}" as="font" type="font/woff2" crossorigin>')
    return "\n".join(pre), "\n".join(css)

def gtm(l):
    """Официальный код Google Tag Manager: (для head, для начала body)."""
    if not GTM_ID or l not in GTM_LANGS:
        return "", ""
    head = ("<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});"
            "var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;"
            "j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})"
            f"(window,document,'script','dataLayer','{GTM_ID}');</script>")
    body = (f'<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={GTM_ID}" '
            'height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>')
    return head, body

def seo(t):
    url = SITE + t["path"]
    p = ['<meta property="og:type" content="website">', f'<meta property="og:title" content="{t["title"]}">',
         f'<meta property="og:description" content="{t["desc"]}">', f'<meta property="og:url" content="{url}">',
         f'<meta property="og:locale" content="{t["locale"]}">']
    if OG_IMAGE:
        p += [f'<meta property="og:image" content="{SITE.rstrip("/") + OG_IMAGE}">', '<meta name="twitter:card" content="summary_large_image">']
    if FAVICON_ICO: p.append(f'<link rel="icon" href="{FAVICON_ICO}" sizes="48x48">')
    if FAVICON: p.append(f'<link rel="icon" href="{FAVICON}" type="image/svg+xml">')
    if APPLE_ICON: p.append(f'<link rel="apple-touch-icon" href="{APPLE_ICON}">')
    if YANDEX_VERIFY: p.append(f'<meta name="yandex-verification" content="{YANDEX_VERIFY}">')
    if GOOGLE_VERIFY: p.append(f'<meta name="google-site-verification" content="{GOOGLE_VERIFY}">')
    ld = {"@context": "https://schema.org", "@type": "Person", "name": t["person"], "jobTitle": t["job"], "url": url, "sameAs": ["https://t.me/tm_glfngr"]}
    p.append('<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>')
    return "\n".join(p)

def build(l):
    global HOME
    t = T[l]; k = 0 if l == "ru" else 1
    HOME = t["home"]
    t = dict(t)   # копия, в которой расставлены неразрывные пробелы
    for key in ("hi", "h1", "lead", "contact_h", "contact_p", "footer", "services_h", "portfolio"):
        t[key] = nb(t[key])
    t["services"] = [(nb(h), nb(p)) for h, p in t["services"]]
    chips = "".join(f'<button class="chip" type="button" data-key="{c}" aria-pressed="{str(c == DEFAULT_CAT).lower()}">{t["cats"][c]}</button>' for c in CATS)
    chips += f'<button class="chip" type="button" data-key="all" aria-pressed="false">{t["all"]}</button>'
    cards, data = [], []
    for i, c in enumerate(CASES):
        title, goal, task, role, result = (nb(x) for x in c[l])
        hid = "" if c["c"] == DEFAULT_CAT else " hidden"
        cards.append(f'<button class="card" type="button" data-i="{i}" data-cat="{c["c"]}"{hid}><div class="thumb"><img src="{url(c["t"])}" alt="" loading="lazy" width="800" height="600"></div><h3>{esc(title)}</h3></button>')
        data.append(dict(title=title, goal=goal, task=task, role=role, result=result, extra=[(nb(a), nb(b)) for a, b in c.get(l + "_extra", [])], img=url(c["i"] or c["t"]), video=(c["i"] or "").lower().endswith(VIDEO_EXT), poster=url(c["t"])))
    services = "".join(f"<li><h3>{h}</h3><p>{p}</p></li>" for h, p in t["services"])
    j = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
    rep = dict(lang=t["lang"], title=t["title"], desc=t["desc"], site=SITE, path=t["path"], dark=DARK, navlabel=t["navlabel"],
               nav0=t["nav"][0], nav1=t["nav"][1], nav2=t["nav"][2], nav3=t["nav"][3], resume_url=esc(t["resume_url"]), msg_url=esc(t["msg_url"]),
               other=t["other"], other_label=t["other_label"], other_label_lc=t["other_label"].lower(), other_title=t["other_title"], theme=t["theme"],
               hi=t["hi"], h1=t["h1"], lead=t["lead"], tg=t["tg"], resume=t["resume"], portfolio=t["portfolio"], filters_label=t["filters"],
               chips=chips, cards="".join(cards), services_h=t["services_h"], services=services, contact_h=t["contact_h"], contact_p=t["contact_p"],
               copy=t["copy"], copied=t["copied"], fail=t["fail"], footer=t["footer"], close=t["close"], prev=t["prev"], next=t["next"],
               cases_json=j(data), labels_json=j(t["labels"]), seo=seo(t), analytics=METRIKA_CODE)
    head, _ = gtm(l)
    analytics = (METRIKA_CODE + "\n" + head).strip()
    rep["analytics"] = ""            # счётчики не стоят в <head>: их подключает скрипт страницы после согласия
    rep["body_start"] = ""
    rep["analytics_json"] = j(analytics)
    names = []
    if METRIKA_CODE.strip(): names.append(CONSENT[l]["yandex"])
    if head: names.append("Google Analytics")
    label, purl = PRIVACY[l]
    rep["privacy"] = f'<a href="{esc(purl)}" target="_blank" rel="noopener">{nb(label)}</a>' if purl else nb(label)
    c = CONSENT[l]
    if names:
        link = f'<a href="{esc(purl)}" target="_blank" rel="noopener">{nb(c["privacy_inline"])}</a>' if purl else nb(c["privacy_inline"])
        before, after = c["text"].split("{privacy}")
        rep["consent_html"] = ('<div class="consent" id="consent" role="dialog" aria-live="polite" hidden>'
                               f'<p>{nb(before.format(services=", ".join(names)))}{link}{nb(after)}</p>'
                               f'<div class="consent-actions"><button class="btn primary" type="button" id="consent-yes">{c["yes"]}</button>'
                               f'<button class="btn" type="button" id="consent-no">{c["no"]}</button></div></div>')
        rep["cookie_link"] = f' · <button class="linkbtn" type="button" id="cookie-settings">{c["settings"]}</button>'
    else:
        rep["consent_html"] = ""
        rep["cookie_link"] = ""
    rep["fonts_head"], rep["fonts_css"] = font_blocks(l)
    html = TEMPLATE
    for key, val in rep.items(): html = html.replace(f"[[{key}]]", val)
    return html

out = pathlib.Path(__file__).parent
(out / "en").mkdir(exist_ok=True)
(out / "index.html").write_text(build("ru"), encoding="utf-8")
(out / "en" / "index.html").write_text(build("en"), encoding="utf-8")
alt = lambda: f'<xhtml:link rel="alternate" hreflang="ru" href="{SITE}"/><xhtml:link rel="alternate" hreflang="en" href="{SITE}en/"/>'
urls = "".join(f"<url><loc>{SITE}{p}</loc>{alt()}</url>" for p in ("", "en/"))
(out / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">' + urls + '</urlset>\n', encoding="utf-8")
(out / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n", encoding="utf-8")
print("ok")
