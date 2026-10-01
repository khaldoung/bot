// /* =========================================================
//    Temp Mailo - Telegram Mini App
//    web/app.js
// ========================================================= */


// /* =========================================================
//    TELEGRAM
// ========================================================= */

// const tg = window.Telegram?.WebApp;

// if (tg) {
//     tg.ready();
//     tg.expand();

//     // جعل لون الواجهة متوافقًا مع Telegram
//     if (tg.setHeaderColor) {
//         tg.setHeaderColor("secondary_bg_color");
//     }

//     if (tg.setBackgroundColor) {
//         tg.setBackgroundColor("bg_color");
//     }
// }


// /* =========================================================
//    GLOBAL STATE
// ========================================================= */

// let currentUser = null;
// let currentLanguage = "ar";


// /* =========================================================
//    API HELPER
// ========================================================= */

// async function api(url, options = {}) {

//     const headers = {
//         "Content-Type": "application/json",
//         ...(options.headers || {})
//     };

//     // Telegram Mini App initData
//     if (tg?.initData) {
//         headers["X-Telegram-Init-Data"] = tg.initData;
//     }

//     const response = await fetch(url, {
//         ...options,
//         headers
//     });

//     let data = null;

//     try {
//         data = await response.json();
//     } catch {
//         data = {};
//     }

//     if (!response.ok) {
//         throw new Error(
//             data?.error ||
//             data?.message ||
//             "Request failed"
//         );
//     }

//     return data;
// }


// /* =========================================================
//    TRANSLATIONS
// ========================================================= */

// const translations = {

//     ar: {

//         welcome: "بريدك المؤقت",

//         currentEmail: "البريد الحالي",

//         copyEmail: "📋 نسخ البريد",

//         copied: "✅ تم نسخ البريد",

//         inbox: "صندوق الوارد",

//         inboxDescription:
//             "عرض الرسائل الواردة",

//         changeEmail:
//             "تغيير البريد",

//         changeEmailDescription:
//             "إنشاء بريد إلكتروني جديد",

//         previousEmails:
//             "البريد السابق",

//         previousEmailsDescription:
//             "عرض الإيميلات السابقة",

//         language:
//             "اللغة",

//         arabic:
//             "العربية",

//         english:
//             "English",

//         loading:
//             "⏳ جاري التحميل...",

//         loadingInbox:
//             "⏳ جاري تحميل الرسائل...",

//         loadingEmails:
//             "⏳ جاري تحميل البريد السابق...",

//         noMessages:
//             "📭 لا توجد رسائل حتى الآن",

//         noPreviousEmails:
//             "🕘 لا توجد إيميلات سابقة",

//         sender:
//             "المرسل",

//         subject:
//             "الموضوع",

//         date:
//             "التاريخ",

//         select:
//             "استخدام",

//         selected:
//             "الحالي",

//         createNew:
//             "🔄 إنشاء بريد جديد",

//         languageChanged:
//             "✅ تم تغيير اللغة",

//         emailChanged:
//             "✅ تم إنشاء بريد جديد",

//         emailSelected:
//             "✅ تم اختيار البريد",

//         error:
//             "❌ حدث خطأ",

//         noEmail:
//             "لا يوجد بريد إلكتروني",

//         confirmChange:
//             "هل تريد إنشاء بريد إلكتروني جديد؟"

//     },


//     en: {

//         welcome:
//             "Your temporary email",

//         currentEmail:
//             "Current email",

//         copyEmail:
//             "📋 Copy email",

//         copied:
//             "✅ Email copied",

//         inbox:
//             "Inbox",

//         inboxDescription:
//             "View received messages",

//         changeEmail:
//             "Change email",

//         changeEmailDescription:
//             "Create a new email address",

//         previousEmails:
//             "Previous emails",

//         previousEmailsDescription:
//             "View previous email addresses",

//         language:
//             "Language",

//         arabic:
//             "العربية",

//         english:
//             "English",

//         loading:
//             "⏳ Loading...",

//         loadingInbox:
//             "⏳ Loading messages...",

//         loadingEmails:
//             "⏳ Loading previous emails...",

//         noMessages:
//             "📭 No messages yet",

//         noPreviousEmails:
//             "🕘 No previous emails",

//         sender:
//             "Sender",

//         subject:
//             "Subject",

//         date:
//             "Date",

//         select:
//             "Use",

//         selected:
//             "Current",

//         createNew:
//             "🔄 Create new email",

//         languageChanged:
//             "✅ Language changed",

//         emailChanged:
//             "✅ New email created",

//         emailSelected:
//             "✅ Email selected",

//         error:
//             "❌ An error occurred",

//         noEmail:
//             "No email address",

//         confirmChange:
//             "Do you want to create a new email?"

//     }

// };


// /* =========================================================
//    TRANSLATION HELPER
// ========================================================= */

// function t(key) {

//     return (
//         translations[currentLanguage]?.[key] ||
//         translations.ar[key] ||
//         key
//     );
// }


// /* =========================================================
//    DOM HELPERS
// ========================================================= */

// function $(id) {
//     return document.getElementById(id);
// }


// function setText(id, text) {

//     const element = $(id);

//     if (element) {
//         element.textContent = text;
//     }
// }


// /* =========================================================
//    TELEGRAM POPUP
// ========================================================= */

// function showPopup(message) {

//     if (tg?.showAlert) {

//         tg.showAlert(message);

//         return;
//     }

//     alert(message);
// }


// /* =========================================================
//    HAPTIC
// ========================================================= */

// function haptic(type = "light") {

//     try {

//         if (
//             tg?.HapticFeedback &&
//             tg.HapticFeedback.impactOccurred
//         ) {
//             tg.HapticFeedback.impactOccurred(type);
//         }

//     } catch {
//         // Ignore haptic errors
//     }
// }


// /* =========================================================
//    LOAD USER
// ========================================================= */

// async function loadUser() {

//     try {

//         setText("currentEmail", t("loading"));

//         const data = await api("/api/me");

//         currentUser = data;

//         if (data.language) {
//             currentLanguage = data.language;
//         }

//         updateInterface();

//     } catch (error) {

//         console.error(error);

//         showError(
//             error.message || t("error")
//         );
//     }
// }


// /* =========================================================
//    UPDATE INTERFACE
// ========================================================= */

// function updateInterface() {

//     document.documentElement.lang =
//         currentLanguage === "ar"
//             ? "ar"
//             : "en";

//     document.documentElement.dir =
//         currentLanguage === "ar"
//             ? "rtl"
//             : "ltr";


//     setText(
//         "welcomeText",
//         t("welcome")
//     );

//     setText(
//         "currentEmailTitle",
//         t("currentEmail")
//     );

//     setText(
//         "copyEmail",
//         t("copyEmail")
//     );

//     setText(
//         "inboxTitle",
//         t("inbox")
//     );

//     setText(
//         "inboxDescription",
//         t("inboxDescription")
//     );

//     setText(
//         "changeEmailTitle",
//         t("changeEmail")
//     );

//     setText(
//         "changeEmailDescription",
//         t("changeEmailDescription")
//     );

//     setText(
//         "previousEmailsTitle",
//         t("previousEmails")
//     );

//     setText(
//         "previousEmailsDescription",
//         t("previousEmailsDescription")
//     );

//     setText(
//         "languageTitle",
//         t("language")
//     );

//     setText(
//         "selectedLanguage",
//         currentLanguage === "ar"
//             ? t("arabic")
//             : t("english")
//     );


//     updateCurrentEmail();
// }


// /* =========================================================
//    CURRENT EMAIL
// ========================================================= */

// function updateCurrentEmail() {

//     const email =
//         currentUser?.email ||
//         currentUser?.current_email ||
//         "";

//     setText(
//         "currentEmail",
//         email || t("noEmail")
//     );
// }


// /* =========================================================
//    COPY EMAIL
// ========================================================= */

// async function copyEmail() {

//     const email =
//         currentUser?.email ||
//         currentUser?.current_email ||
//         "";

//     if (!email) {

//         showPopup(t("noEmail"));

//         return;
//     }


//     try {

//         await navigator.clipboard.writeText(email);

//         haptic("light");

//         showPopup(t("copied"));

//     } catch {

//         // Fallback for older browsers
//         try {

//             const textarea =
//                 document.createElement("textarea");

//             textarea.value = email;

//             document.body.appendChild(textarea);

//             textarea.select();

//             document.execCommand("copy");

//             textarea.remove();

//             showPopup(t("copied"));

//         } catch {

//             showPopup(email);
//         }
//     }
// }


// /* =========================================================
//    INBOX
// ========================================================= */

// async function loadInbox() {

//     showLoading(t("loadingInbox"));

//     try {

//         const data =
//             await api("/api/inbox");

//         renderInbox(
//             data.messages ||
//             data.inbox ||
//             []
//         );

//     } catch (error) {

//         console.error(error);

//         showError(
//             error.message || t("error")
//         );
//     }
// }


// /* =========================================================
//    RENDER INBOX
// ========================================================= */

// function renderInbox(messages) {

//     const content = $("content");

//     if (!content) {
//         return;
//     }


//     if (!messages.length) {

//         content.innerHTML = `
//             <div class="content-card">
//                 <div class="empty">
//                     ${t("noMessages")}
//                 </div>
//             </div>
//         `;

//         return;
//     }


//     content.innerHTML = `
//         <div class="content-card">
//             <h2>
//                 📥 ${escapeHTML(t("inbox"))}
//             </h2>
//         </div>

//         ${messages.map(message => {

//             const subject =
//                 message.subject ||
//                 "(No subject)";

//             const sender =
//                 message.from ||
//                 message.sender ||
//                 "";

//             const body =
//                 message.body ||
//                 message.text ||
//                 "";

//             const date =
//                 message.created_at ||
//                 message.createdAt ||
//                 message.date ||
//                 "";

//             return `
//                 <div class="message-card">

//                     <div class="message-subject">
//                         ${escapeHTML(subject)}
//                     </div>

//                     <div class="message-from">
//                         ${escapeHTML(sender)}
//                     </div>

//                     <div class="message-body">
//                         ${escapeHTML(body)}
//                     </div>

//                     ${
//                         date
//                             ? `
//                             <div class="message-from">
//                                 ${escapeHTML(
//                                     formatDate(date)
//                                 )}
//                             </div>
//                             `
//                             : ""
//                     }

//                 </div>
//             `;

//         }).join("")}
//     `;
// }


// /* =========================================================
//    CHANGE EMAIL
// ========================================================= */

// async function changeEmail() {

//     const confirmed =
//         confirm(t("confirmChange"));

//     if (!confirmed) {
//         return;
//     }


//     showLoading(t("loading"));


//     try {

//         const data =
//             await api(
//                 "/api/change-email",
//                 {
//                     method: "POST"
//                 }
//             );


//         currentUser = {
//             ...(currentUser || {}),
//             ...(data.user || {}),
//             email:
//                 data.email ||
//                 data.user?.email ||
//                 currentUser?.email
//         };


//         updateCurrentEmail();

//         haptic("medium");

//         showPopup(t("emailChanged"));

//         clearContent();

//     } catch (error) {

//         console.error(error);

//         showError(
//             error.message || t("error")
//         );
//     }
// }


// /* =========================================================
//    PREVIOUS EMAILS
// ========================================================= */

// async function loadPreviousEmails() {

//     showLoading(t("loadingEmails"));


//     try {

//         const data =
//             await api("/api/previous-emails");

//         renderPreviousEmails(
//             data.accounts ||
//             data.emails ||
//             []
//         );

//     } catch (error) {

//         console.error(error);

//         showError(
//             error.message || t("error")
//         );
//     }
// }


// /* =========================================================
//    RENDER PREVIOUS EMAILS
// ========================================================= */

// function renderPreviousEmails(accounts) {

//     const content = $("content");

//     if (!content) {
//         return;
//     }


//     if (!accounts.length) {

//         content.innerHTML = `
//             <div class="content-card">
//                 <div class="empty">
//                     ${t("noPreviousEmails")}
//                 </div>
//             </div>
//         `;

//         return;
//     }


//     content.innerHTML = `
//         <div class="content-card">

//             <h2>
//                 🕘 ${escapeHTML(
//                     t("previousEmails")
//                 )}
//             </h2>

//             <div class="email-list">

//                 ${accounts.map(account => {

//                     const email =
//                         account.email ||
//                         "";

//                     const isCurrent =
//                         account.is_current === true ||
//                         account.isCurrent === true;


//                     return `
//                         <div class="email-item">

//                             <div class="email-item-info">

//                                 <div class="email-item-address">
//                                     ${escapeHTML(email)}
//                                 </div>

//                                 ${
//                                     account.created_at
//                                         ? `
//                                         <div class="email-item-date">
//                                             ${escapeHTML(
//                                                 formatDate(
//                                                     account.created_at
//                                                 )
//                                             )}
//                                         </div>
//                                         `
//                                         : ""
//                                 }

//                             </div>

//                             ${
//                                 isCurrent
//                                     ? `
//                                         <button
//                                             class="select-email"
//                                             disabled
//                                         >
//                                             ${escapeHTML(
//                                                 t("selected")
//                                             )}
//                                         </button>
//                                     `
//                                     : `
//                                         <button
//                                             class="select-email"
//                                             onclick="selectEmail(${Number(account.id)})"
//                                         >
//                                             ${escapeHTML(
//                                                 t("select")
//                                             )}
//                                         </button>
//                                     `
//                             }

//                         </div>
//                     `;

//                 }).join("")}

//             </div>

//         </div>
//     `;
// }


// /* =========================================================
//    SELECT PREVIOUS EMAIL
// ========================================================= */

// async function selectEmail(id) {

//     if (!id) {
//         return;
//     }


//     showLoading(t("loading"));


//     try {

//         const data =
//             await api(
//                 "/api/select-email",
//                 {
//                     method: "POST",

//                     body: JSON.stringify({
//                         account_id: id
//                     })
//                 }
//             );


//         currentUser = {
//             ...(currentUser || {}),
//             ...(data.user || {}),
//             email:
//                 data.email ||
//                 data.user?.email ||
//                 currentUser?.email
//         };


//         updateCurrentEmail();

//         haptic("medium");

//         showPopup(t("emailSelected"));

//         clearContent();

//     } catch (error) {

//         console.error(error);

//         showError(
//             error.message || t("error")
//         );
//     }
// }


// /* =========================================================
//    LANGUAGE
// ========================================================= */

// function showLanguage() {

//     const content = $("content");

//     if (!content) {
//         return;
//     }


//     content.innerHTML = `
//         <div class="content-card">

//             <h2>
//                 🌐 ${escapeHTML(
//                     t("language")
//                 )}
//             </h2>

//             <div class="language-options">

//                 <button
//                     class="language-option ${
//                         currentLanguage === "ar"
//                             ? "active"
//                             : ""
//                     }"
//                     onclick="changeLanguage('ar')"
//                 >
//                     🇾🇪 العربية
//                 </button>


//                 <button
//                     class="language-option ${
//                         currentLanguage === "en"
//                             ? "active"
//                             : ""
//                     }"
//                     onclick="changeLanguage('en')"
//                 >
//                     🇬🇧 English
//                 </button>

//             </div>

//         </div>
//     `;
// }


// /* =========================================================
//    CHANGE LANGUAGE
// ========================================================= */

// async function changeLanguage(language) {

//     if (
//         language !== "ar" &&
//         language !== "en"
//     ) {
//         return;
//     }


//     try {

//         await api(
//             "/api/language",
//             {
//                 method: "POST",

//                 body: JSON.stringify({
//                     language: language
//                 })
//             }
//         );


//         currentLanguage = language;


//         if (currentUser) {
//             currentUser.language = language;
//         }


//         updateInterface();

//         showLanguage();

//         haptic("light");

//     } catch (error) {

//         console.error(error);

//         showError(
//             error.message || t("error")
//         );
//     }
// }


// /* =========================================================
//    LOADING
// ========================================================= */

// function showLoading(message) {

//     const content = $("content");

//     if (!content) {
//         return;
//     }


//     content.innerHTML = `
//         <div class="content-card">

//             <div class="loading">
//                 ${escapeHTML(message)}
//             </div>

//         </div>
//     `;
// }


// /* =========================================================
//    ERROR
// ========================================================= */

// function showError(message) {

//     const content = $("content");

//     if (!content) {
//         return;
//     }


//     content.innerHTML = `
//         <div class="error">
//             ${escapeHTML(message)}
//         </div>
//     `;
// }


// /* =========================================================
//    CLEAR CONTENT
// ========================================================= */

// function clearContent() {

//     const content = $("content");

//     if (!content) {
//         return;
//     }


//     content.innerHTML = "";
// }


// /* =========================================================
//    DATE FORMAT
// ========================================================= */

// function formatDate(value) {

//     if (!value) {
//         return "";
//     }


//     try {

//         const date =
//             new Date(value);

//         if (
//             Number.isNaN(
//                 date.getTime()
//             )
//         ) {
//             return String(value);
//         }


//         return new Intl.DateTimeFormat(
//             currentLanguage === "ar"
//                 ? "ar-YE"
//                 : "en-US",
//             {
//                 dateStyle: "medium",
//                 timeStyle: "short"
//             }
//         ).format(date);

//     } catch {

//         return String(value);
//     }
// }


// /* =========================================================
//    HTML ESCAPE
// ========================================================= */

// function escapeHTML(value) {

//     if (
//         value === null ||
//         value === undefined
//     ) {
//         return "";
//     }


//     return String(value)
//         .replaceAll("&", "&amp;")
//         .replaceAll("<", "&lt;")
//         .replaceAll(">", "&gt;")
//         .replaceAll('"', "&quot;")
//         .replaceAll("'", "&#039;");
// }


// /* =========================================================
//    BUTTON EVENTS
// ========================================================= */

// document.addEventListener(
//     "DOMContentLoaded",
//     () => {

//         const copyButton =
//             $("copyEmail");

//         if (copyButton) {

//             copyButton.addEventListener(
//                 "click",
//                 copyEmail
//             );
//         }


//         const inboxButton =
//             $("inboxButton");

//         if (inboxButton) {

//             inboxButton.addEventListener(
//                 "click",
//                 loadInbox
//             );
//         }


//         const changeEmailButton =
//             $("changeEmailButton");

//         if (changeEmailButton) {

//             changeEmailButton.addEventListener(
//                 "click",
//                 changeEmail
//             );
//         }


//         const previousEmailsButton =
//             $("previousEmailsButton");

//         if (previousEmailsButton) {

//             previousEmailsButton.addEventListener(
//                 "click",
//                 loadPreviousEmails
//             );
//         }


//         const languageButton =
//             $("languageButton");

//         if (languageButton) {

//             languageButton.addEventListener(
//                 "click",
//                 showLanguage
//             );
//         }


//         loadUser();
//     }
// );


// /* =========================================================
//    MAKE FUNCTIONS AVAILABLE
//    TO INLINE BUTTONS
// ========================================================= */

// window.selectEmail =
//     selectEmail;

// window.changeLanguage =
//     changeLanguage;



/* =========================================================
   Temp Mailo - Telegram Mini App
   web/app.js
========================================================= */


/* =========================================================
   TELEGRAM
========================================================= */

const tg = window.Telegram?.WebApp;

if (tg) {

    tg.ready();
    tg.expand();

    if (tg.setHeaderColor) {
        tg.setHeaderColor("secondary_bg_color");
    }

    if (tg.setBackgroundColor) {
        tg.setBackgroundColor("bg_color");
    }
}


/* =========================================================
   GLOBAL STATE
========================================================= */

let currentUser = null;
let currentLanguage = "ar";


/* =========================================================
   API HELPER
========================================================= */

async function api(url, options = {}) {

    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {})
    };

    // Telegram Mini App initData
    if (tg?.initData) {
        headers["X-Telegram-Init-Data"] = tg.initData;
    }

    const response = await fetch(url, {
        ...options,
        headers
    });

    let data = null;

    try {
        data = await response.json();
    } catch {
        data = {};
    }

    if (!response.ok) {
        throw new Error(
            data?.error ||
            data?.message ||
            "Request failed"
        );
    }

    return data;
}


/* =========================================================
   TRANSLATIONS
========================================================= */

const translations = {

    ar: {

        welcome: "بريدك المؤقت",

        currentEmail: "البريد الحالي",

        copyEmail: "📋 نسخ البريد",

        copied: "✅ تم نسخ البريد",

        inbox: "صندوق الوارد",

        inboxDescription:
            "عرض الرسائل الواردة",

        language:
            "اللغة",

        arabic:
            "العربية",

        english:
            "English",

        loading:
            "⏳ جاري التحميل...",

        loadingInbox:
            "⏳ جاري تحميل الرسائل...",

        noMessages:
            "📭 لا توجد رسائل حتى الآن",

        error:
            "❌ حدث خطأ",

        noEmail:
            "لا يوجد بريد إلكتروني"
    },


    en: {

        welcome:
            "Your temporary email",

        currentEmail:
            "Current email",

        copyEmail:
            "📋 Copy email",

        copied:
            "✅ Email copied",

        inbox:
            "Inbox",

        inboxDescription:
            "View received messages",

        language:
            "Language",

        arabic:
            "العربية",

        english:
            "English",

        loading:
            "⏳ Loading...",

        loadingInbox:
            "⏳ Loading messages...",

        noMessages:
            "📭 No messages yet",

        error:
            "❌ An error occurred",

        noEmail:
            "No email address"
    }

};


/* =========================================================
   TRANSLATION HELPER
========================================================= */

function t(key) {

    return (
        translations[currentLanguage]?.[key] ||
        translations.ar[key] ||
        key
    );
}


/* =========================================================
   DOM HELPERS
========================================================= */

function $(id) {

    return document.getElementById(id);
}


function setText(id, text) {

    const element = $(id);

    if (element) {
        element.textContent = text;
    }
}


/* =========================================================
   TELEGRAM POPUP
========================================================= */

function showPopup(message) {

    if (tg?.showAlert) {

        tg.showAlert(message);

        return;
    }

    alert(message);
}


/* =========================================================
   HAPTIC
========================================================= */

function haptic(type = "light") {

    try {

        if (
            tg?.HapticFeedback &&
            tg.HapticFeedback.impactOccurred
        ) {

            tg.HapticFeedback.impactOccurred(type);
        }

    } catch {
        // Ignore haptic errors
    }
}


/* =========================================================
   LOAD USER
========================================================= */

async function loadUser() {

    try {

        setText(
            "currentEmail",
            t("loading")
        );

        const data =
            await api("/api/me");

        currentUser = data;

        if (data.language) {
            currentLanguage = data.language;
        }

        updateInterface();

    } catch (error) {

        console.error(error);

        showError(
            error.message || t("error")
        );
    }
}


/* =========================================================
   UPDATE INTERFACE
========================================================= */

function updateInterface() {

    document.documentElement.lang =
        currentLanguage === "ar"
            ? "ar"
            : "en";

    document.documentElement.dir =
        currentLanguage === "ar"
            ? "rtl"
            : "ltr";


    setText(
        "welcomeText",
        t("welcome")
    );


    setText(
        "currentEmailTitle",
        t("currentEmail")
    );


    setText(
        "copyEmail",
        t("copyEmail")
    );


    setText(
        "inboxTitle",
        t("inbox")
    );


    setText(
        "inboxDescription",
        t("inboxDescription")
    );


    setText(
        "languageTitle",
        t("language")
    );


    setText(
        "selectedLanguage",
        currentLanguage === "ar"
            ? t("arabic")
            : t("english")
    );


    updateCurrentEmail();
}


/* =========================================================
   CURRENT EMAIL
========================================================= */

function updateCurrentEmail() {

    const email =
        currentUser?.email ||
        currentUser?.current_email ||
        "";

    setText(
        "currentEmail",
        email || t("noEmail")
    );
}


/* =========================================================
   COPY EMAIL
========================================================= */

async function copyEmail() {

    const email =
        currentUser?.email ||
        currentUser?.current_email ||
        "";

    if (!email) {

        showPopup(
            t("noEmail")
        );

        return;
    }


    try {

        await navigator.clipboard.writeText(email);

        haptic("light");

        showPopup(
            t("copied")
        );

    } catch {

        // Fallback for older browsers

        try {

            const textarea =
                document.createElement("textarea");

            textarea.value = email;

            document.body.appendChild(
                textarea
            );

            textarea.select();

            document.execCommand("copy");

            textarea.remove();

            showPopup(
                t("copied")
            );

        } catch {

            showPopup(email);
        }
    }
}


/* =========================================================
   INBOX
========================================================= */

async function loadInbox() {

    showLoading(
        t("loadingInbox")
    );

    try {

        const data =
            await api("/api/inbox");

        renderInbox(
            data.messages ||
            data.inbox ||
            []
        );

    } catch (error) {

        console.error(error);

        showError(
            error.message || t("error")
        );
    }
}


/* =========================================================
   RENDER INBOX
========================================================= */

function renderInbox(messages) {

    const content =
        $("content");

    if (!content) {
        return;
    }


    if (!messages.length) {

        content.innerHTML = `
            <div class="content-card">

                <div class="empty">
                    ${escapeHTML(
                        t("noMessages")
                    )}
                </div>

            </div>
        `;

        return;
    }


    content.innerHTML = `
        <div class="content-card">

            <h2>
                📥 ${escapeHTML(
                    t("inbox")
                )}
            </h2>

        </div>


        ${messages.map(message => {

            const subject =
                message.subject ||
                "(No subject)";

            const sender =
                message.from ||
                message.sender ||
                "";

            const body =
                message.body ||
                message.text ||
                "";

            const date =
                message.created_at ||
                message.createdAt ||
                message.date ||
                "";


            return `
                <div class="message-card">

                    <div class="message-subject">
                        ${escapeHTML(subject)}
                    </div>


                    <div class="message-from">
                        ${escapeHTML(sender)}
                    </div>


                    <div class="message-body">
                        ${escapeHTML(body)}
                    </div>


                    ${
                        date
                            ? `
                            <div class="message-from">
                                ${escapeHTML(
                                    formatDate(date)
                                )}
                            </div>
                            `
                            : ""
                    }

                </div>
            `;

        }).join("")}
    `;
}


/* =========================================================
   LANGUAGE
========================================================= */

function showLanguage() {

    const content =
        $("content");

    if (!content) {
        return;
    }


    content.innerHTML = `
        <div class="content-card">

            <h2>
                🌐 ${escapeHTML(
                    t("language")
                )}
            </h2>


            <div class="language-options">

                <button
                    class="language-option ${
                        currentLanguage === "ar"
                            ? "active"
                            : ""
                    }"
                    onclick="changeLanguage('ar')"
                >
                    🇾🇪 العربية
                </button>


                <button
                    class="language-option ${
                        currentLanguage === "en"
                            ? "active"
                            : ""
                    }"
                    onclick="changeLanguage('en')"
                >
                    🇬🇧 English
                </button>

            </div>

        </div>
    `;
}


/* =========================================================
   CHANGE LANGUAGE
========================================================= */

async function changeLanguage(language) {

    if (
        language !== "ar" &&
        language !== "en"
    ) {
        return;
    }


    try {

        await api(
            "/api/language",
            {
                method: "POST",

                body: JSON.stringify({
                    language: language
                })
            }
        );


        currentLanguage =
            language;


        if (currentUser) {
            currentUser.language =
                language;
        }


        updateInterface();

        showLanguage();

        haptic("light");

    } catch (error) {

        console.error(error);

        showError(
            error.message || t("error")
        );
    }
}


/* =========================================================
   LOADING
========================================================= */

function showLoading(message) {

    const content =
        $("content");

    if (!content) {
        return;
    }


    content.innerHTML = `
        <div class="content-card">

            <div class="loading">
                ${escapeHTML(message)}
            </div>

        </div>
    `;
}


/* =========================================================
   ERROR
========================================================= */

function showError(message) {

    const content =
        $("content");

    if (!content) {
        return;
    }


    content.innerHTML = `
        <div class="error">
            ${escapeHTML(message)}
        </div>
    `;
}


/* =========================================================
   DATE FORMAT
========================================================= */

function formatDate(value) {

    if (!value) {
        return "";
    }


    try {

        const date =
            new Date(value);


        if (
            Number.isNaN(
                date.getTime()
            )
        ) {

            return String(value);
        }


        return new Intl.DateTimeFormat(

            currentLanguage === "ar"
                ? "ar-YE"
                : "en-US",

            {
                dateStyle: "medium",
                timeStyle: "short"
            }

        ).format(date);

    } catch {

        return String(value);
    }
}


/* =========================================================
   HTML ESCAPE
========================================================= */

function escapeHTML(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";
    }


    return String(value)

        .replaceAll(
            "&",
            "&amp;"
        )

        .replaceAll(
            "<",
            "&lt;"
        )

        .replaceAll(
            ">",
            "&gt;"
        )

        .replaceAll(
            '"',
            "&quot;"
        )

        .replaceAll(
            "'",
            "&#039;"
        );
}


/* =========================================================
   BUTTON EVENTS
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        /* -----------------------------------------
           COPY EMAIL
        ----------------------------------------- */

        const copyButton =
            $("copyEmail");

        if (copyButton) {

            copyButton.addEventListener(
                "click",
                copyEmail
            );
        }


        /* -----------------------------------------
           INBOX
        ----------------------------------------- */

        const inboxButton =
            $("inboxButton");

        if (inboxButton) {

            inboxButton.addEventListener(
                "click",
                loadInbox
            );
        }


        /* -----------------------------------------
           LANGUAGE
        ----------------------------------------- */

        const languageButton =
            $("languageButton");

        if (languageButton) {

            languageButton.addEventListener(
                "click",
                showLanguage
            );
        }


        /* -----------------------------------------
           LOAD USER
        ----------------------------------------- */

        loadUser();
    }
);


/* =========================================================
   MAKE LANGUAGE AVAILABLE
   TO INLINE BUTTONS
========================================================= */

window.changeLanguage =
    changeLanguage;
