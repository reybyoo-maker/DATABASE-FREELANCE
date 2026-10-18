import argparse, hashlib, json, logging, os, re, sys, time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from urllib.parse import urlparse
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
L = logging.getLogger("database-freelance")
TZ = ZoneInfo("Asia/Jakarta")
UA = "DATABASE-FREELANCE/1.0 public business research"
SOCIAL = {"instagram.com":"instagram","facebook.com":"facebook","fb.com":"facebook","linkedin.com":"linkedin","tiktok.com":"tiktok","x.com":"other_social","twitter.com":"other_social","youtube.com":"other_social","threads.net":"other_social"}
REGIONS = [
("Jakarta","Indonesia"),("Bandung","Indonesia"),("Surabaya","Indonesia"),("Yogyakarta","Indonesia"),("Medan","Indonesia"),("Makassar","Indonesia"),("Bali","Indonesia"),
("Kuala Lumpur","Malaysia"),("Singapore","Singapore"),("Bangkok","Thailand"),("Manila","Philippines"),("Hanoi","Vietnam"),("Tokyo","Japan"),("Seoul","South Korea"),("Taipei","Taiwan"),("Delhi","India"),("Dubai","United Arab Emirates"),("Istanbul","Turkey"),("Berlin","Germany"),("Paris","France"),("London","United Kingdom"),("Amsterdam","Netherlands"),("Madrid","Spain"),("Milan","Italy"),("New York","United States"),("Toronto","Canada"),("Mexico City","Mexico"),("Sao Paulo","Brazil"),("Sydney","Australia"),("Nairobi","Kenya"),("Cape Town","South Africa"),("Lagos","Nigeria"),("Auckland","New Zealand")]
SECTORS = ["restaurant","hotel","beauty salon","fitness studio","dental clinic","real estate agency","marketing agency","accounting firm","law firm","e-commerce brand","fashion store","furniture store","car dealership","travel agency","education company","software company","IT services company","construction company","interior design studio","event organizer","logistics company","manufacturer","medical clinic","coworking space","consulting firm","retail shop","photography studio","wedding vendor"]
DOMAINS = [("instagram.com","Instagram"),("facebook.com","Facebook"),("linkedin.com/company","LinkedIn"),("tiktok.com","TikTok")]
LANGUAGE = {
"Indonesia":("Indonesian","Halo tim {name}, saya menemukan profil publik {name} di {city}, {country}. Ada kemungkinan saya dapat membantu meningkatkan {service} agar {benefit}. Apakah saya boleh mengirimkan beberapa ide yang relevan? Jika tidak sesuai, beri tahu saya dan saya tidak akan menindaklanjuti."),
"Japan":("Japanese","{name} ご担当者様、突然のご連絡失礼いたします。公開情報を拝見し、{service} の改善を通じて {benefit} に貢献できる可能性があると感じました。具体的なアイデアをお送りしてもよろしいでしょうか。ご不要でしたらお知らせください。"),
"South Korea":("Korean","{name} 담당자님 안녕하세요. 공개된 정보를 살펴보던 중 연락드립니다. {service} 개선을 통해 {benefit}에 도움을 드릴 수 있을 것 같아 맞춤형 아이디어를 공유드려도 될지 문의드립니다. 원치 않으시면 알려주세요."),
"China":("Chinese","{name} 团队您好！我在研究 {city} 的企业时看到了贵公司的公开资料。优化 {service} 或许能帮助贵公司实现 {benefit}。方便的话，我可以发送几条建议吗？如不需要，请告知，我不会继续联系。"),
"Taiwan":("Chinese","{name} 團隊您好！我在研究 {city} 的企業時看到了貴公司的公開資料。改善 {service} 或許能協助貴公司達成 {benefit}。方便的話，我可以分享幾個建議嗎？若不需要請告知，我不會繼續聯絡。"),
"Thailand":("Thai","สวัสดีทีมงาน {name} ผมพบข้อมูลสาธารณะของธุรกิจคุณใน {city} อาจมีโอกาสปรับปรุง {service} เพื่อช่วย {benefit} ขออนุญาตส่งแนวคิดที่เหมาะกับธุรกิจได้ไหมครับ หากไม่สะดวกแจ้งได้เลยครับ"),
"Vietnam":("Vietnamese","Xin chào đội ngũ {name}, tôi tìm thấy thông tin công khai của doanh nghiệp tại {city}. Có thể có cơ hội cải thiện {service} để hỗ trợ {benefit}. Tôi có thể gửi một vài ý tưởng phù hợp không? Nếu không phù hợp, vui lòng cho tôi biết."),
"Germany":("German","Guten Tag, liebes Team von {name}. Bei meiner Recherche zu Unternehmen in {city}, {country} bin ich auf Ihr öffentliches Profil gestoßen. Möglicherweise lässt sich {service} verbessern, um {benefit}. Darf ich Ihnen einige Ideen schicken? Falls nicht, geben Sie mir bitte Bescheid."),
"France":("French","Bonjour à l’équipe de {name}, j’ai découvert votre profil public à {city}, {country}. Il pourrait être intéressant d’améliorer {service} afin de {benefit}. Puis-je vous envoyer quelques idées adaptées ? Si cela ne vous intéresse pas, dites-le-moi et je ne vous relancerai pas."),
"Spain":("Spanish","Hola, equipo de {name}. Encontré su perfil público en {city}, {country}. Puede haber una oportunidad para mejorar {service} y ayudar a {benefit}. ¿Puedo compartir algunas ideas adaptadas? Si no les interesa, avísenme y no insistiré."),
"Mexico":("Spanish","Hola, equipo de {name}. Encontré su perfil público en {city}, {country}. Puede haber una oportunidad para mejorar {service} y ayudar a {benefit}. ¿Puedo compartir algunas ideas? Si no les interesa, avísenme y no insistiré."),
"Brazil":("Portuguese","Olá, equipe da {name}. Encontrei o perfil público da empresa em {city}, {country}. Pode haver uma oportunidade de melhorar {service} e ajudar {benefit}. Posso compartilhar algumas ideias? Se não fizer sentido, é só avisar e não voltarei a contactar."),
"Italy":("Italian","Buongiorno team di {name}, ho trovato il vostro profilo pubblico a {city}, {country}. Potrebbe esserci un'opportunità per migliorare {service} e contribuire a {benefit}. Posso condividere qualche idea? Se non vi interessa, fatemelo sapere."),
"Netherlands":("Dutch","Hallo team van {name}, ik kwam uw openbare bedrijfsprofiel tegen in {city}, {country}. Mogelijk is er een kans om {service} te verbeteren en te helpen bij {benefit}. Mag ik enkele ideeën delen? Laat het weten als dit niet relevant is."),
"Malaysia":("Malay","Salam pasukan {name}, saya menemui profil perniagaan awam anda di {city}, {country}. Mungkin ada peluang untuk menambah baik {service} bagi membantu {benefit}. Bolehkah saya berkongsi beberapa idea yang sesuai? Jika tidak relevan, beritahu saya dan saya tidak akan menghubungi lagi."),
"United Arab Emirates":("Arabic","مرحباً بفريق {name}، اطّلعت على المعلومات العامة لنشاطكم في {city}، {country}. قد تكون هناك فرصة لتحسين {service} للمساعدة في {benefit}. هل يناسبكم أن أشارك بعض الأفكار المخصصة؟ إذا لم يكن ذلك مناسباً، أخبروني ولن أتابع التواصل."),
"Saudi Arabia":("Arabic","مرحباً بفريق {name}، اطّلعت على المعلومات العامة لنشاطكم في {city}، {country}. قد تكون هناك فرصة لتحسين {service} للمساعدة في {benefit}. هل يناسبكم أن أشارك بعض الأفكار المخصصة؟ إذا لم يكن ذلك مناسباً، أخبروني ولن أتابع التواصل."),
"Egypt":("Arabic","مرحباً بفريق {name}، وجدت ملف نشاطكم المنشور علناً في {city}، {country}. قد توجد فرصة لتحسين {service} للمساعدة في {benefit}. هل يمكنني إرسال بعض الأفكار المناسبة لنشاطكم؟ إذا لم يكن ذلك مناسباً، أخبروني ولن أتابع التواصل."),
"Turkey":("Turkish","Merhaba {name} ekibi, {city}, {country} bölgesindeki işletmeleri araştırırken herkese açık işletme profilinizi buldum. {benefit} amacıyla {service} alanında bir iyileştirme fırsatı olabilir. İşletmenize özel birkaç fikir paylaşmam uygun olur mu? İlgilenmiyorsanız lütfen bildirin; tekrar iletişime geçmem."),
"Portugal":("Portuguese","Olá, equipa da {name}. Encontrei o perfil público da empresa em {city}, {country}. Pode haver uma oportunidade de melhorar {service} e ajudar {benefit}. Posso partilhar algumas ideias personalizadas? Se não for relevante, diga-me e não voltarei a contactar."),
"Argentina":("Spanish","Hola, equipo de {name}. Encontré su perfil público en {city}, {country}. Puede haber una oportunidad para mejorar {service} y ayudar a {benefit}. ¿Puedo compartir algunas ideas adaptadas? Si no les interesa, avísenme y no insistiré."),
"Colombia":("Spanish","Hola, equipo de {name}. Encontré su perfil público en {city}, {country}. Puede haber una oportunidad para mejorar {service} y ayudar a {benefit}. ¿Puedo compartir algunas ideas adaptadas? Si no les interesa, avísenme y no insistiré."),
"Chile":("Spanish","Hola, equipo de {name}. Encontré su perfil público en {city}, {country}. Puede haber una oportunidad para mejorar {service} y ayudar a {benefit}. ¿Puedo compartir algunas ideas adaptadas? Si no les interesa, avísenme y no insistiré."),
"Peru":("Spanish","Hola, equipo de {name}. Encontré su perfil público en {city}, {country}. Puede haber una oportunidad para mejorar {service} y ayudar a {benefit}. ¿Puedo compartir algunas ideas adaptadas? Si no les interesa, avísenme y no insistiré."),
"Morocco":("French","Bonjour à l’équipe de {name}, j’ai découvert votre profil public à {city}, {country}. Il pourrait être intéressant d’améliorer {service} afin de {benefit}. Puis-je vous envoyer quelques idées adaptées ? Si cela ne vous intéresse pas, dites-le-moi et je ne vous relancerai pas."),
"Singapore":("English","Hello {name} team, I came across your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"Philippines":("English","Hello {name} team, I found your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"India":("English","Hello {name} team, I came across your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"United States":("English","Hello {name} team, I came across your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"United Kingdom":("English","Hello {name} team, I came across your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"Canada":("English","Hello {name} team, I came across your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"Australia":("English","Hello {name} team, I came across your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"New Zealand":("English","Hello {name} team, I came across your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"Kenya":("English","Hello {name} team, I came across your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"South Africa":("English","Hello {name} team, I came across your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"Nigeria":("English","Hello {name} team, I came across your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"Ghana":("English","Hello {name} team, I came across your public business profile in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up."),
"Saudi Arabia":("Arabic","مرحباً بفريق {name}، اطّلعت على المعلومات العامة لنشاطكم في {city}، {country}. قد تكون هناك فرصة لتحسين {service} للمساعدة في {benefit}. هل يناسبكم أن أشارك بعض الأفكار المخصصة؟ إذا لم يكن ذلك مناسباً، أخبروني ولن أتابع التواصل."),

}
DEFAULT = ("English","Hello {name} team, I came across your public business profile while researching companies in {city}, {country}. There may be an opportunity to improve {service} and help {benefit}. Would you be open to a few tailored ideas? If this is not relevant, please let me know and I will not follow up.")

PORTFOLIO_CATALOG = {
    "b2b_leads": {
        "title": "Pencari calon pelanggan untuk jasa bisnis",
        "url": "https://agencyai.reybyoo.workers.dev/portfolio/jasa-b2b-lead-engine",
        "service_id": "sistem pencarian calon klien B2B, penilaian kecocokan prospek, dan pengaturan follow-up",
        "benefit_id": "tim sales dapat memprioritaskan prospek yang lebih sesuai dan mengurangi follow-up yang terlewat",
        "service_en": "a B2B lead workflow that finds potential clients, scores fit, and organizes follow-ups",
        "benefit_en": "help sales prioritize relevant prospects and keep follow-ups organized",
    },
    "customer_chat": {
        "title": "Asisten chat toko skincare",
        "url": "https://agencyai.reybyoo.workers.dev/portfolio/toko-skincare-chat-ai",
        "service_id": "asisten AI WhatsApp untuk menjawab pertanyaan umum produk dan pemesanan, mencatat pesanan di Google Sheets, serta meneruskan chat rumit ke staf",
        "benefit_id": "pertanyaan rutin lebih konsisten tertangani dan pesanan lebih rapi tanpa semua chat harus dijawab manual",
        "service_en": "an AI WhatsApp assistant that answers common product and order questions, logs orders in Google Sheets, and hands complex chats to staff",
        "benefit_en": "handle routine questions more consistently and keep orders organized without manually answering every message",
    },
    "email_campaign": {
        "title": "Daftar calon pembeli + email promosi",
        "url": "https://agencyai.reybyoo.workers.dev/portfolio/daftar-email-campaign",
        "service_id": "pengelolaan daftar prospek yang rapi dan draf email promosi yang dipersonalisasi dengan opsi berhenti menerima pesan",
        "benefit_id": "tim dapat mengelompokkan calon pembeli dan menyiapkan tindak lanjut yang lebih relevan",
        "service_en": "organized prospect lists and personalized email campaign drafts with an opt-out option",
        "benefit_en": "help the team segment prospects and prepare more relevant follow-ups",
    },
    "brand_content": {
        "title": "Sistem konten brand fashion",
        "url": "https://agencyai.reybyoo.workers.dev/portfolio/brand-fashion-content",
        "service_id": "sistem konten AI untuk menyusun kalender konten, caption, dan skrip sesuai gaya brand",
        "benefit_id": "tim memiliki ide konten terencana dan lebih mudah menjaga konsistensi komunikasi brand",
        "service_en": "an AI content workflow that prepares a content calendar, captions, and scripts in the brand's style",
        "benefit_en": "make content planning more consistent and reduce the time spent starting each post from scratch",
    },
    "instagram_dm": {
        "title": "Balas komentar & DM Instagram",
        "url": "https://agencyai.reybyoo.workers.dev/portfolio/dm-instagram-otomatis",
        "service_id": "otomatisasi jawaban untuk pertanyaan umum dari komentar dan DM Instagram, dengan pertanyaan khusus tetap diteruskan ke manusia",
        "benefit_id": "mengurangi pesan yang terlewat sambil menjaga pertanyaan yang membutuhkan penilaian manusia tetap ditangani staf",
        "service_en": "Instagram comment and DM automation for common questions, with unusual or sensitive queries handed to a person",
        "benefit_en": "help reduce missed messages while keeping nuanced questions with the human team",
    },
    "reservations": {
        "title": "Reservasi meja lewat chat",
        "url": "https://agencyai.reybyoo.workers.dev/portfolio/reservasi-restoran",
        "service_id": "alur reservasi lewat WhatsApp yang mencatat jadwal secara otomatis dan menyiapkan pengingat sebelum waktu reservasi",
        "benefit_id": "permintaan reservasi lebih teratur dan staf tidak perlu menyalin setiap jadwal secara manual",
        "service_en": "a WhatsApp reservation workflow that records bookings and prepares reminders before the appointment",
        "benefit_en": "keep booking details organized and reduce manual copying of reservations",
    },
    "store_faq": {
        "title": "Bot jawab pertanyaan & cek pesanan",
        "url": "https://agencyai.reybyoo.workers.dev/portfolio/faq-toko-online",
        "service_id": "bot AI untuk menjawab FAQ dan pertanyaan status pesanan, lalu meneruskan kasus yang rumit ke admin",
        "benefit_id": "pelanggan dapat jawaban untuk pertanyaan berulang dan admin dapat fokus pada kasus yang memerlukan bantuan langsung",
        "service_en": "an AI FAQ and order-status bot that answers recurring questions and hands complex cases to staff",
        "benefit_en": "answer recurring customer questions more consistently while leaving complex cases with the admin team",
    },
    "sales_reporting": {
        "title": "Rekap penjualan harian UMKM",
        "url": "https://agencyai.reybyoo.workers.dev/portfolio/rekap-penjualan-umkm",
        "service_id": "otomatisasi pengumpulan data penjualan ke Google Sheets dan pengiriman ringkasan harian kepada pemilik",
        "benefit_id": "mengurangi rekap manual dan membuat ringkasan penjualan lebih mudah ditinjau",
        "service_en": "automated sales-data collection into Google Sheets and a daily summary for the business owner",
        "benefit_en": "reduce manual sales reconciliation and make sales summaries easier to review",
    },
    "competitor_research": {
        "title": "Pantau pesaing otomatis",
        "url": "https://agencyai.reybyoo.workers.dev/portfolio/riset-kompetitor",
        "service_id": "pemantauan informasi publik pesaing seperti perubahan harga dan promosi, lalu merangkumnya secara berkala",
        "benefit_id": "tim dapat meninjau perubahan pasar tanpa mengumpulkan semua informasi pesaing secara manual",
        "service_en": "a public-source competitor monitoring workflow that summarizes visible changes in prices and promotions",
        "benefit_en": "review market changes without manually collecting every competitor update",
    },
    "payment_reminders": {
        "title": "Pengingat tagihan yang sopan",
        "url": "https://agencyai.reybyoo.workers.dev/portfolio/pengingat-tagihan",
        "service_id": "pengingat pembayaran terjadwal dengan bahasa yang sopan dan pencatatan status di Google Sheets",
        "benefit_id": "tindak lanjut tagihan lebih konsisten tanpa harus menyusun setiap pengingat dari awal",
        "service_en": "scheduled, polite payment reminders with status tracking in Google Sheets",
        "benefit_en": "keep payment follow-ups consistent without drafting every reminder manually",
    },
    "daily_reporting": {
        "title": "Laporan harian ke Telegram",
        "url": "https://agencyai.reybyoo.workers.dev/portfolio/laporan-harian-telegram",
        "service_id": "otomatisasi pengingat janji dan pengiriman ringkasan operasional harian kepada staf terkait",
        "benefit_id": "informasi rutin lebih mudah diterima tepat waktu dan laporan tidak perlu dikompilasi manual setiap hari",
        "service_en": "automated appointment reminders and daily operational summaries sent to the appropriate staff",
        "benefit_en": "deliver routine information on time and reduce manual daily reporting",
    },
}
EXAMPLE_LINK_LABEL = {
    "Indonesian": "Contoh ilustrasi solusi yang relevan",
    "Malay": "Contoh ilustrasi penyelesaian yang berkaitan",
    "English": "Related illustrative workflow",
    "Japanese": "関連する仕組みのイメージ例",
    "Korean": "관련 자동화 예시",
    "Chinese": "相关工作流程示例",
    "Thai": "ตัวอย่างเวิร์กโฟลว์ที่เกี่ยวข้อง",
    "Vietnamese": "Ví dụ quy trình liên quan",
    "German": "Passendes illustratives Workflow-Beispiel",
    "French": "Exemple illustratif de workflow pertinent",
    "Spanish": "Ejemplo ilustrativo de flujo relevante",
    "Portuguese": "Exemplo ilustrativo de fluxo relacionado",
    "Italian": "Esempio illustrativo di flusso pertinente",
    "Dutch": "Relevant illustratief workflowvoorbeeld",
    "Arabic": "مثال توضيحي لسير عمل ذي صلة",
    "Turkish": "İlgili iş akışı örneği",
}
LOCALIZED_FALLBACK = {
    "Indonesian": ("sistem AI untuk membantu alur kerja seperti contoh yang relevan di portofolio kami", "mengurangi pekerjaan berulang dan merapikan tindak lanjut pelanggan atau penjualan"),
    "Malay": ("aliran kerja AI seperti contoh yang berkaitan dalam portfolio kami", "mengurangkan kerja berulang dan menyusun susulan pelanggan atau jualan"),
    "English": ("an AI workflow like the relevant example in our portfolio", "reduce repetitive work and organize customer or sales follow-ups"),
    "Japanese": ("ポートフォリオの関連例のようなAI業務自動化", "定型作業を減らし、顧客対応や営業フォローを整理する"),
    "Korean": ("포트폴리오의 관련 예시와 같은 AI 업무 자동화", "반복 업무를 줄이고 고객 문의와 영업 후속 관리를 체계화하는"),
    "Chinese": ("与我们作品集相关示例类似的 AI 工作流程自动化", "减少重复工作并更有条理地处理客户咨询或销售跟进"),
    "Thai": ("ระบบงานอัตโนมัติด้วย AI ตามตัวอย่างที่เกี่ยวข้องในผลงานของเรา", "ลดงานซ้ำและจัดระเบียบการติดตามลูกค้าหรือการขาย"),
    "Vietnamese": ("quy trình tự động hóa bằng AI tương tự ví dụ liên quan trong hồ sơ năng lực của chúng tôi", "giảm việc lặp lại và sắp xếp việc chăm sóc khách hàng hoặc theo dõi bán hàng"),
    "German": ("einen KI-Workflow wie das passende Beispiel in unserem Portfolio", "wiederkehrende Aufgaben reduzieren und Kundenanfragen oder Vertriebsnachfassaktionen strukturieren"),
    "French": ("un workflow d'IA comme l'exemple pertinent de notre portfolio", "réduire les tâches répétitives et mieux organiser les demandes clients ou les relances commerciales"),
    "Spanish": ("un flujo de trabajo con IA como el ejemplo relacionado de nuestro portafolio", "reducir tareas repetitivas y organizar mejor las consultas de clientes o el seguimiento comercial"),
    "Portuguese": ("um fluxo de trabalho com IA como o exemplo relacionado do nosso portfólio", "reduzir tarefas repetitivas e organizar melhor as consultas dos clientes ou o acompanhamento comercial"),
    "Italian": ("un flusso di lavoro con IA come l'esempio pertinente del nostro portfolio", "ridurre le attività ripetitive e organizzare meglio le richieste dei clienti o i follow-up commerciali"),
    "Dutch": ("een AI-workflow zoals het relevante voorbeeld in ons portfolio", "herhaalwerk verminderen en klantvragen of verkoopopvolging beter organiseren"),
    "Arabic": ("سير عمل بالذكاء الاصطناعي مثل المثال ذي الصلة في معرض أعمالنا", "تقليل المهام المتكررة وتنظيم استفسارات العملاء أو متابعة المبيعات"),
    "Turkish": ("portföyümüzdeki ilgili örneğe benzer bir yapay zekâ iş akışı", "tekrarlayan işleri azaltmak ve müşteri taleplerini veya satış takibini düzenlemek"),
}
def choose_portfolio_offer(p):
    """Select the closest real example page on the agency site based on sector and public evidence."""
    industry = s(p.get("industry", ""), 200).lower()
    blob = " ".join(s(p.get(k, ""), 800) for k in ("company_name", "industry", "evidence", "source_name")).lower()
    socials = any(p.get(k) for k in ("instagram", "facebook", "tiktok"))
    def has(*words):
        return any(word in blob or word in industry for word in words)
    if has("skincare", "cosmetic product", "cosmetics brand", "makeup store", "beauty product", "beauty e-commerce"):
        key = "customer_chat"
    elif has("fashion", "clothing", "apparel", "garment", "boutique", "jewelry", "fashion store", "fashion brand"):
        key = "brand_content"
    elif has("freelancer", "freelance", "invoice", "payment reminder", "billing", "accounting", "bookkeeping"):
        key = "payment_reminders"
    elif has("clinic", "dental", "dentist", "medical", "hospital", "physiotherapy", "healthcare"):
        key = "daily_reporting"
    elif has("hotel", "travel agency", "tour operator", "wedding", "event organizer", "salon", "spa", "fitness studio", "gym"):
        key = "reservations"
    elif has("restaurant", "cafe", "coffee shop", "coffee", "catering", "bar", "food and beverage", "food service"):
        key = "instagram_dm" if socials else "reservations"
    elif has("e-commerce", "ecommerce", "online store", "online shop", "retail shop", "retail store", "electronics store", "furniture store", "car dealership", "shop", "store", "retail", "distributor", "wholesale"):
        key = "store_faq" if has("online", "e-commerce", "ecommerce", "shop", "store") else "sales_reporting"
    elif has("real estate", "property", "property agency", "marketing agency", "consulting firm", "law firm", "software company", "it services", "logistics", "manufacturer", "manufacturing", "construction", "accounting firm", "b2b", "business service"):
        key = "email_campaign" if has("real estate", "property") else "b2b_leads"
    elif has("startup", "brand", "marketing", "content", "photography", "design studio"):
        key = "competitor_research" if has("startup", "competitor", "market research") else "brand_content"
    elif socials:
        key = "instagram_dm"
    else:
        key = "b2b_leads"
    offer = PORTFOLIO_CATALOG[key]
    p["portfolio_service_match"] = offer["title"]
    p["portfolio_example_title"] = offer["title"]
    p["relevant_portfolio_url"] = offer["url"]
    return offer

AGENCY_PORTFOLIO_URL = "https://agencyai.reybyoo.workers.dev/"
AGENCY_NAME = "AGA-Ai Growth Agency"

# The sender is a member of the marketing team; [nama kamu] must be replaced manually before sending.
OUTREACH_INTRO = {
    "Indonesian": "Perkenalkan, saya [nama kamu] dari AGA-Ai Growth Agency.",
    "Malay": "Salam, saya [nama kamu] daripada AGA-Ai Growth Agency.",
    "English": "Hi, I'm [nama kamu] from AGA-Ai Growth Agency.",
    "Japanese": "はじめまして。AGA-Ai Growth Agencyの[nama kamu]と申します。",
    "Korean": "안녕하세요. AGA-Ai Growth Agency의 [nama kamu]입니다.",
    "Chinese": "您好，我是 AGA-Ai Growth Agency 的[nama kamu]。",
    "Thai": "สวัสดีครับ/ค่ะ ผม/ดิฉัน [nama kamu] จาก AGA-Ai Growth Agency",
    "Vietnamese": "Xin chào, tôi là [nama kamu] từ AGA-Ai Growth Agency.",
    "German": "Guten Tag, ich bin [nama kamu] von AGA-Ai Growth Agency.",
    "French": "Bonjour, je suis [nama kamu] de AGA-Ai Growth Agency.",
    "Spanish": "Hola, soy [nama kamu] de AGA-Ai Growth Agency.",
    "Portuguese": "Olá, sou [nama kamu] da AGA-Ai Growth Agency.",
    "Italian": "Buongiorno, sono [nama kamu] di AGA-Ai Growth Agency.",
    "Dutch": "Hallo, ik ben [nama kamu] van AGA-Ai Growth Agency.",
    "Arabic": "مرحباً، أنا [nama kamu] من AGA-Ai Growth Agency.",
    "Turkish": "Merhaba, ben AGA-Ai Growth Agency'den [nama kamu].",
}
PORTFOLIO_LABEL = {
    "Indonesian": "Portofolio kami",
    "Malay": "Portfolio kami",
    "Japanese": "ポートフォリオ",
    "Korean": "포트폴리오",
    "Chinese": "作品集 / Portfolio",
    "Thai": "ผลงาน / Portfolio",
    "Vietnamese": "Hồ sơ năng lực / Portfolio",
    "German": "Portfolio",
    "French": "Portfolio",
    "Spanish": "Portafolio",
    "Portuguese": "Portfólio",
    "Italian": "Portfolio",
    "Dutch": "Portfolio",
    "Arabic": "نماذج أعمالنا / Portfolio",
    "Turkish": "Portföy",
}

def add_agency_context(message, language, example_url="", example_title=""):
    """Ensure outreach introduces the marketing employee and links the matching illustrative portfolio example."""
    message = s(message, 3000).strip()
    intro = OUTREACH_INTRO.get(language, OUTREACH_INTRO["English"])
    # Keep the recipient greeting first, then introduce the employee and agency.
    if "[nama kamu]" not in message.lower() or AGENCY_NAME.lower() not in message.lower():
        greeting_end = re.search(r"[.!?。！？؟]\s*", message[:220])
        if greeting_end:
            message = message[:greeting_end.end()].rstrip() + " " + intro + (" " + message[greeting_end.end():].lstrip() if message[greeting_end.end():].strip() else "")
        else:
            message = intro + ("\n\n" + message if message else "")
    if AGENCY_PORTFOLIO_URL not in message:
        label = PORTFOLIO_LABEL.get(language, "Portfolio")
        message = message.rstrip() + f"\n\n{label}: {AGENCY_PORTFOLIO_URL}"
    if example_url and example_url not in message and example_url != AGENCY_PORTFOLIO_URL:
        label = EXAMPLE_LINK_LABEL.get(language, EXAMPLE_LINK_LABEL["English"])
        message = message.rstrip() + f"\n\n{label} — {example_title}: {example_url}"
    return message

OSM = [
("Jakarta","Indonesia",-6.2088,106.8456),("Bandung","Indonesia",-6.9175,107.6191),("Surabaya","Indonesia",-7.2575,112.7521),("Yogyakarta","Indonesia",-7.7956,110.3695),
("Kuala Lumpur","Malaysia",3.139,101.6869),("Singapore","Singapore",1.3521,103.8198),("Bangkok","Thailand",13.7563,100.5018),("Manila","Philippines",14.5995,120.9842),
("Tokyo","Japan",35.6762,139.6503),("Delhi","India",28.6139,77.209),("Dubai","United Arab Emirates",25.2048,55.2708),("London","United Kingdom",51.5072,-0.1276),
("Berlin","Germany",52.52,13.405),("Paris","France",48.8566,2.3522),("New York","United States",40.7128,-74.006),("Toronto","Canada",43.6532,-79.3832),
("Sydney","Australia",-33.8688,151.2093),("Sao Paulo","Brazil",-23.5505,-46.6333)]
def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def s(v,n=1000): return re.sub(r"\s+"," ",str(v or "")).strip()[:n]
def url(v):
    v=s(v,500).strip("()[]{}<>,.;\"'")
    if not v: return ""
    if not v.startswith(("http://","https://")): v="https://"+v
    p=urlparse(v)
    return v if p.netloc and "." in p.netloc else ""
def host(v): return (urlparse(v).hostname or "").lower().removeprefix("www.")
def social_type(v):
    h=host(v)
    for d,k in SOCIAL.items():
        if h==d or h.endswith("."+d): return k
    return ""
def urls(text):
    return list(dict.fromkeys(url(x) for x in re.findall(r"https?://[^\s<>\"']+",str(text or ""),re.I) if url(x)))
def socials(text):
    d={k:"" for k in ["instagram","facebook","linkedin","tiktok","other_social"]}
    for u in urls(text):
        k=social_type(u)
        if k and not d[k]: d[k]=u
    return d
def whatsapp(text):
    for u in urls(text):
        if host(u) in ("wa.me","api.whatsapp.com","web.whatsapp.com","whatsapp.com") or host(u).endswith(".whatsapp.com"): return u
    return ""
def mail(text):
    m=re.findall(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",str(text or ""))
    return m[0] if m else ""
def phone(text):
    for x in re.findall(r"\+?\d[\d ()-]{7,}\d",str(text or "")):
        if 8<=len(re.sub(r"\D","",x))<=15: return x
    return ""
def pid(name,country,key): return hashlib.sha256(f"{name.lower().strip()}|{country.lower().strip()}|{key.lower().strip()}".encode()).hexdigest()[:18]
def make_record(name,country,city,industry,website,wa,phone_v,email,soc,source,source_name,evidence):
    if not wa and not any(soc.values()): return None
    identity_scope=f"{city}|{industry}"
    return {"prospect_id":pid(name,country,identity_scope),"company_name":name,"country":country,"city":city,"industry":industry,
      "website":website,"whatsapp_url":wa,"public_phone":phone_v,"public_email":email,**soc,
      "source_url":source,"source_name":source_name,"evidence":s(evidence,1200),"discovered_at_utc":now(),
      "outreach_language":"","need_audit":"","recommended_service":"","prospect_score":0,"prospect_grade":"MEDIUM",
      "grade_reason":"","outreach_dm":"","outreach_email_subject":"","outreach_email_body":"","outreach_whatsapp":"","data_quality":"Public source; verify before contact"}
def tavily(key,query):
    r=requests.post("https://api.tavily.com/search",json={"api_key":key,"query":query,"search_depth":"advanced","topic":"general","max_results":10,"include_answer":False,"include_raw_content":False},headers={"User-Agent":UA},timeout=35)
    if r.status_code==429: L.warning("Tavily rate limit/quota reached"); return []
    r.raise_for_status(); return r.json().get("results",[])
def discover_web(key,wanted):
    out={}
    if not key: L.warning("TAVILY_API_KEY missing; only OSM discovery is available"); return []
    dt=datetime.now(TZ); start=(dt.timetuple().tm_yday*5+dt.hour//6*7)%len(REGIONS)
    for i in range(min(12,max(4,(wanted+7)//8))):
        city,country=REGIONS[(start+i)%len(REGIONS)]; sector=SECTORS[(dt.timetuple().tm_yday*3+(dt.hour//6)*5+i*7)%len(SECTORS)]
        domain,platform=DOMAINS[(i+dt.hour//6)%len(DOMAINS)]
        query=f'site:{domain} "{sector}" "{city}" "{country}" business company official contact'
        try: results=tavily(key,query)
        except Exception as e: L.warning("Tavily error %s: %s",platform,s(e,180)); continue
        L.info("Tavily %s: %s result(s) for %s, %s",platform,len(results),city,country)
        for z in results:
            u=url(z.get("url","")); title=s(z.get("title"),160); snippet=s(z.get("content"),900)
            if not u or not title or title.lower() in {"instagram","facebook","linkedin","tiktok","home","homepage","log in","sign up"}: continue
            combined=f"{title}. {snippet}. {u}"; soc=socials(combined); sk=social_type(u)
            if sk in soc: soc[sk]=soc[sk] or u
            wa=whatsapp(combined)
            if not wa and not any(soc.values()): continue
            name=re.sub(r"\s*[|–-]\s*(Instagram|Facebook|LinkedIn|TikTok|Official.*)$","",title,flags=re.I).strip()
            name=re.sub(r"\s*\(@[^)]*\)","",name).strip()
            if len(name)<2: continue
            website="" if sk else u
            row=make_record(name,country,city,sector,website,wa,phone(snippet),mail(combined),soc,u,f"Tavily Search / {platform}",f"Title: {title}. Snippet: {snippet}")
            if row: out.setdefault(row["prospect_id"],row)
        time.sleep(.25)
        if len(out)>=min(wanted*2,150): break
    return list(out.values())
def overpass_query(lat,lon):
    keys=["contact:instagram","instagram","contact:facebook","facebook","contact:linkedin","linkedin","contact:tiktok","tiktok","contact:whatsapp","whatsapp","contact:youtube","youtube"]
    sel="\n".join(f'nwr(around:9000,{lat},{lon})["name"]["{k}"];' for k in keys)
    return f"[out:json][timeout:30];(\n{sel}\n);out center tags 180;"
def discover_osm(wanted):
    out={}; dt=datetime.now(TZ); start=(dt.timetuple().tm_yday*3+dt.hour//6*5)%len(OSM)
    for city,country,lat,lon in [OSM[(start+i)%len(OSM)] for i in range(min(8,len(OSM)))]:
        try:
            r=requests.post("https://overpass-api.de/api/interpreter",data={"data":overpass_query(lat,lon)},headers={"User-Agent":UA},timeout=45)
            if r.status_code in (429,502,503,504): L.warning("Overpass HTTP %s at %s",r.status_code,city); continue
            r.raise_for_status(); els=r.json().get("elements",[])
        except Exception as e: L.warning("Overpass error at %s: %s",city,s(e,180)); continue
        L.info("OSM/Overpass: %s tagged record(s) around %s",len(els),city)
        for el in els:
            tags=el.get("tags",{}); name=s(tags.get("name"),160)
            if len(name)<2: continue
            soc={k:"" for k in ["instagram","facebook","linkedin","tiktok","other_social"]}; wa=""
            keys={"instagram":["contact:instagram","instagram"],"facebook":["contact:facebook","facebook"],"linkedin":["contact:linkedin","linkedin"],"tiktok":["contact:tiktok","tiktok"],"other_social":["contact:youtube","youtube","contact:x","twitter","x"]}
            for field,alts in keys.items():
                for k in alts:
                    raw=tags.get(k)
                    if raw:
                        v=url(str(raw))
                        if v and (social_type(v) or k in ("instagram","facebook","linkedin","tiktok","youtube","twitter","x")): soc[field]=soc[field] or v
            for k in ("contact:whatsapp","whatsapp"):
                raw=tags.get(k,"")
                if raw:
                    v=url(str(raw))
                    if v and ("whatsapp" in host(v) or host(v)=="wa.me"): wa=v
                    else:
                        digits=re.sub(r"\D","",str(raw))
                        if 8<=len(digits)<=15: wa="https://wa.me/"+digits
            website=url(tags.get("contact:website") or tags.get("website") or "")
            kind=tags.get("shop") or tags.get("office") or tags.get("craft") or tags.get("amenity") or tags.get("tourism") or tags.get("leisure") or "Business"
            osm_url=f"https://www.openstreetmap.org/{el.get('type','node')}/{el.get('id','')}"
            row=make_record(name,country,city,s(kind,100),website,wa,tags.get("contact:phone") or tags.get("phone",""),tags.get("contact:email") or tags.get("email",""),soc,osm_url,"OpenStreetMap / Overpass",json.dumps(tags,ensure_ascii=False))
            if row: out.setdefault(row["prospect_id"],row)
        time.sleep(2)
        if len(out)>=min(wanted*2,150): break
    return list(out.values())
def gemini(prompt,key,model):
    # Never include request URLs or exception strings in logs: the URL contains the API key.
    try:
        r=requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
           json={"contents":[{"role":"user","parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.25,"responseMimeType":"application/json"}},
           headers={"User-Agent":UA,"x-goog-api-key":key},timeout=(5,12))
    except requests.RequestException as exc:
        raise RuntimeError(f"Gemini transport failure ({type(exc).__name__})") from None
    if r.status_code==404: raise RuntimeError(f"Gemini model {model} was not found; configure GEMINI_MODEL")
    if r.status_code==429: raise RuntimeError("Gemini API quota/rate limit hit (HTTP 429)")
    if not 200 <= r.status_code < 300:
        raise RuntimeError(f"Gemini API returned HTTP {r.status_code}")
    try:
        parts=r.json().get("candidates",[{}])[0].get("content",{}).get("parts",[])
        text="".join(x.get("text","") for x in parts)
    except (ValueError,TypeError,KeyError,IndexError) as exc:
        raise RuntimeError(f"Gemini response parse failed ({type(exc).__name__})") from None
    text=re.sub(r"^\x60{3}(?:json)?\s*|\s*\x60{3}$","",text.strip(),flags=re.I)
    a,b=text.find("{"),text.rfind("}")
    if a<0 or b<=a: raise RuntimeError("Gemini response was not JSON")
    return json.loads(text[a:b+1])
def template_fallback(p,err):
    offer=choose_portfolio_offer(p)
    lang,tmpl=LANGUAGE.get(p["country"],DEFAULT)
    if lang=="Indonesian":
        service,benefit=offer["service_id"],offer["benefit_id"]
        recommended=offer["service_id"]
    elif lang=="English":
        service,benefit=offer["service_en"],offer["benefit_en"]
        recommended=offer["service_en"]
    else:
        service,benefit=LOCALIZED_FALLBACK.get(lang,LOCALIZED_FALLBACK["English"])
        recommended=offer["service_en"]
    draft=tmpl.format(name=p["company_name"],city=p["city"],country=p["country"],service=service,benefit=benefit)
    # Contact-channel availability alone is not enough to assign the top tier.
    score=38+bool(p.get("whatsapp_url"))*8+bool(p.get("public_email"))*6+bool(p.get("website"))*6+sum(bool(p.get(k)) for k in ("instagram","facebook","linkedin","tiktok"))*3
    score=min(74,score)
    p.update(outreach_language=lang,need_audit="AI analysis was unavailable, so a company-specific need has not been verified. The suggested offer was matched from the agency's public portfolio based on the prospect's sector; verify the fit before contacting. Fallback reason: "+s(err,120),recommended_service=recommended,prospect_score=score,prospect_grade="MEDIUM" if score>=45 else "LOW",grade_reason="Fallback rating based on public contact availability only. Not evidence of buying intent; manual review required.",outreach_dm=draft,outreach_whatsapp=draft,outreach_email_subject=f"Ideas for {p['company_name']}",outreach_email_body=draft,data_quality=p.get("data_quality","")+"; AI unavailable; fallback analysis")
    for key in ("outreach_dm","outreach_whatsapp","outreach_email_body"):
        p[key]=add_agency_context(p.get(key,""),p.get("outreach_language",lang),p.get("relevant_portfolio_url",""),p.get("portfolio_example_title",""))
def analyze(p,key,model):
    lang,_=LANGUAGE.get(p["country"],DEFAULT)
    offer=choose_portfolio_offer(p)
    facts={k:p.get(k,"") for k in ("company_name","country","city","industry","website","whatsapp_url","public_email","public_phone","instagram","facebook","linkedin","tiktok","other_social","source_url","source_name","evidence")}
    offer_context={"matched_service":offer["title"],"service_description":offer["service_en"],"potential_benefit":offer["benefit_en"],"relevant_illustrative_example_url":offer["url"],"agency_homepage":AGENCY_PORTFOLIO_URL}
    prompt=f"""You are a careful B2B outreach researcher for AGA-Ai Growth Agency. The agency website at {AGENCY_PORTFOLIO_URL} showcases AI and workflow services including: WhatsApp customer chat assistants that answer common questions and log orders; FAQ and order-status bots; Instagram comment/DM automation; B2B lead discovery and prospect fit scoring; personalized email campaign preparation; AI content calendars, captions and scripts; WhatsApp reservation recording and reminders; sales data reporting to Google Sheets; public-source competitor monitoring; polite scheduled payment reminders; and daily operational summaries.
Analyze ONLY the supplied public company evidence; never invent business needs, budget, buying intent, results, or facts. If evidence is thin, say so. Use the provided portfolio match as a relevant OFFER TO EXPLORE, not as proof that the company has that problem. JSON only with: need_audit (2-4 sentences, clearly distinguish observed facts from a possible opportunity), recommended_service (1-2 specific services that match the selected portfolio example), prospect_score (integer 0-100; evidence specificity 35%, fit 25%, public contact usability 25%, data quality 15%), prospect_grade (RECOMMENDED for 75-100, MEDIUM for 45-74, LOW for 0-44), grade_reason, outreach_language (use {lang} unless evidence supports another language), outreach_dm, outreach_email_subject, outreach_email_body, outreach_whatsapp. Write all four messages in outreach_language; keep them personal to this sector and specific to the selected portfolio solution, briefly explain what workflow the agency can help configure, and ask permission to share a tailored idea. Do not claim the example is a real client result: portfolio project pages explicitly say examples are illustrative. Do not make up company problems, metrics, client results or prior contact. Keep the contact respectful and include a brief opt-out. Do NOT add sender introduction, agency name, homepage URL, or project link inside the model draft; the application will append the staff intro and both links consistently. Company facts: {json.dumps(facts,ensure_ascii=False)}. Best-fit portfolio offer: {json.dumps(offer_context,ensure_ascii=False)}"""
    try:
        d=gemini(prompt,key,model); score=max(0,min(100,int(float(d.get("prospect_score",45)))))
        grade="RECOMMENDED" if score>=75 else ("MEDIUM" if score>=45 else "LOW")
        for k in ("need_audit","recommended_service","grade_reason","outreach_dm","outreach_email_subject","outreach_email_body","outreach_whatsapp","outreach_language"): p[k]=s(d.get(k),2500)
        p["prospect_score"]=score; p["prospect_grade"]=grade
        if not p["need_audit"] or not p["outreach_dm"]: raise ValueError("Required AI fields missing")
        for key in ("outreach_dm","outreach_whatsapp","outreach_email_body"):
            p[key]=add_agency_context(p.get(key,""),p.get("outreach_language") or lang,p.get("relevant_portfolio_url",""),p.get("portfolio_example_title",""))
    except Exception as e:
        L.warning("AI fallback for %s: %s",p["company_name"],s(e,180)); template_fallback(p,str(e))
def sheet(url_,token,payload):
    r=requests.post(url_,json={"token":token,**payload},headers={"User-Agent":UA},timeout=45); r.raise_for_status()
    d=r.json()
    if not d.get("ok"): raise RuntimeError("Sheet endpoint error: "+s(d,300))
    return d
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--dry-run",action="store_true"); args=ap.parse_args()
    tk=os.getenv("TAVILY_API_KEY","").strip(); gk=os.getenv("GEMINI_API_KEY","").strip()
    wh=os.getenv("SHEET_WEBHOOK_URL","").strip(); token=os.getenv("WEBHOOK_TOKEN","").strip()
    model=os.getenv("GEMINI_MODEL","gemini-3.5-flash-lite").strip()
    try: target=max(1,min(500,int(os.getenv("DAILY_TARGET","100"))))
    except ValueError: target=100
    if not gk: L.error("GEMINI_API_KEY is required"); return 2
    if not args.dry_run and (not wh or not token): L.error("SHEET_WEBHOOK_URL and WEBHOOK_TOKEN are required"); return 2
    daily=0
    if not args.dry_run:
        try: daily=int(sheet(wh,token,{"action":"stats"}).get("daily_count",0))
        except Exception as e: L.error("Could not read Sheet stats: %s",s(e,250)); return 3
        L.info("Jakarta daily total %d/%d",daily,target)
        if daily>=target: L.info("Daily target already met"); return 0
    wanted=target if args.dry_run else target-daily
    pool={}
    for batch in (discover_web(tk,wanted),discover_osm(wanted)):
        for p in batch: pool.setdefault(p["prospect_id"],p)
    rows=list(pool.values())
    rows.sort(key=lambda p:(bool(p["whatsapp_url"]),bool(p["public_email"]),sum(bool(p[k]) for k in ("instagram","facebook","linkedin","tiktok","other_social")),bool(p["website"])),reverse=True)
    if args.dry_run:
        # Keep dry runs bounded; their output is a sample, not an upload.
        rows=rows[:20]
    else:
        # Cap each run so a temporary AI outage cannot prevent all Sheet exports.
        # Four scheduled runs/day can process up to 120 rows if fresh unique candidates exist.
        rows=rows[:min(30,max(1,(target-daily)*2))]
    L.info("Qualified distinct prospects discovered: %d; selected for this run: %d",len(pool),len(rows))
    if args.dry_run:
        for p in rows: analyze(p,gk,model)
        print(json.dumps(rows,ensure_ascii=False,indent=2))
        L.info("Dry run only; no rows uploaded")
        return 0
    inserted=0
    # Analyze and write in small batches. Completed batches remain in Sheets if a later batch fails.
    for start in range(0,len(rows),10):
        batch=rows[start:start+10]
        for p in batch:
            analyze(p,gk,model)
        try:
            result=sheet(wh,token,{"action":"append","prospects":batch,"run_id":now()})
            inserted += int(result.get("inserted",0))
            daily=int(result.get("daily_count",daily+int(result.get("inserted",0))))
            L.info("Sheets batch %d/%d: inserted=%s; daily total=%d/%d",start//10+1,(len(rows)+9)//10,result.get("inserted",0),daily,target)
            if daily>=target:
                L.info("Daily target met")
                break
        except Exception as e:
            L.error("Google Sheets append failed (%s)",type(e).__name__)
            return 4
    if daily<target: L.warning("TARGET GAP: %d records short today. Next scheduled run will continue.",target-daily)
    L.info("Run finished: inserted=%d this run; daily total=%d/%d.",inserted,daily,target)
    return 0
if __name__=="__main__": sys.exit(main())
