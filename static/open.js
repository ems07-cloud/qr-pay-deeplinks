// static/open.js
document.addEventListener("DOMContentLoaded", function () {
    const statusEl = document.getElementById("status");
    const errorEl = document.getElementById("error");

    function setStatus(text) {
        if (statusEl) statusEl.textContent = text;
    }

    function setError(text) {
        if (errorEl) errorEl.textContent = text;
    }

    function detectOS() {
        const ua = navigator.userAgent.toLowerCase();
        if (/iphone|ipad|ipod/.test(ua)) return "ios";
        if (/android/.test(ua)) return "android";
        return "unknown";
    }

    // Парсим путь /open/{bank}/{invoice_id}
    const parts = window.location.pathname.split("/").filter(Boolean);
    // ожидаем ["open", "bank", "invoice"]
    if (parts.length < 3 || parts[0] !== "open") {
        setError("Некорректный формат ссылки.");
        return;
    }

    const bank = parts[1];
    const invoiceId = decodeURIComponent(parts[2]);

    const os = detectOS();
    if (os === "unknown") {
        setError("Не удалось автоматически определить вашу ОС. Откройте ссылку с устройства iOS или Android.");
        return;
    }

    setStatus("Определена ОС: " + os + ". Получаем ссылки для открытия приложения...");

    const url =
        "/api/v1/get_links?bank=" +
        encodeURIComponent(bank) +
        "&os=" +
        encodeURIComponent(os) +
        "&invoice=" +
        encodeURIComponent(invoiceId);

    fetch(url)
        .then((resp) => {
            if (!resp.ok) {
                throw new Error("Ошибка сервера: " + resp.status);
            }
            return resp.json();
        })
        .then((data) => {
            const links = (data && data.links) || [];
            if (!Array.isArray(links) || links.length === 0) {
                setError("Для этого банка пока нет ссылок. Установите приложение банка или попробуйте позже.");
                return;
            }
            setStatus("Пробуем открыть приложение...");
            openLinksSequentially(links, 0);
        })
        .catch((err) => {
            console.error(err);
            setError("Не удалось получить ссылки. Попробуйте позже.");
        });

    function openLinksSequentially(links, index) {
        if (index >= links.length) {
            setError("Не удалось открыть приложение. Установите приложение банка.");
            return;
        }

        const link = links[index];
        setStatus("Пробуем открыть приложение (вариант " + (index + 1) + " из " + links.length + ")...");

        const before = Date.now();

        const timeout = setTimeout(function () {
            const elapsed = Date.now() - before;
            // Если страница всё ещё видима — считаем, что приложение не открылось
            if (!document.hidden) {
                openLinksSequentially(links, index + 1);
            } else {
                // Страница стала скрыта → скорее всего пользователь ушёл в приложение
                // Ничего больше не делаем.
            }
        }, 1000); // 1000 мс — в диапазоне 800–1200 мс по ТЗ

        try {
            window.location.href = link;
        } catch (e) {
            console.error("Ошибка открытия ссылки", e);
            clearTimeout(timeout);
            openLinksSequentially(links, index + 1);
        }
    }
});
