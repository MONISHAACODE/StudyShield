
function updateBlockedWebsites() {
    fetch("http://127.0.0.1:8000/api/blocked-websites/", {
        credentials: "include"
    })
    .then(async response => {
        if (!response.ok) {
            throw new Error("Blocked websites API: " + response.status);
        }
        return response.json();
    })
    .then(data => {
        const blockedWebsites = (
            data.blocked_websites || []
        ).map(site =>
            site.trim().toLowerCase().replace(/^www\./, "")
        );

        chrome.storage.local.set({ blockedWebsites });
        console.log("Blocked Websites:", blockedWebsites);
    })
    .catch(error => console.error("API Error:", error));
}

// Record a blocked attempt only once per message
function recordDistraction(website) {
    const formData = new URLSearchParams();
    formData.append("website", website);

    fetch("http://127.0.0.1:8000/api/record-distraction/", {
        method: "POST",
        credentials: "include",
        body: formData
    })
    .then(async response => {
        const contentType = response.headers.get("content-type") || "";

        if (!contentType.includes("application/json")) {
            throw new Error("Login or API response issue");
        }

        const data = await response.json();

        if (!response.ok || !data.success) {
            console.error("Distraction not saved:", data);
            return;
        }

        console.log("Distraction Recorded:", data);
    })
    .catch(error =>
        console.error("Distraction API Error:", error)
    );
}

// Only content.js reports blocked attempts
chrome.runtime.onMessage.addListener((message, sender) => {
    if (
        message.type === "STUDY_SHIELD_BLOCKED" &&
        sender.tab &&
        sender.tab.url
    ) {
        try {
            const hostname = new URL(sender.tab.url)
                .hostname.toLowerCase().replace(/^www\./, "");

            const reported = String(message.website || "")
                .toLowerCase().replace(/^www\./, "");

            if (hostname === reported) {
                recordDistraction(hostname);
            }
        } catch (error) {
            console.error("Invalid blocked URL:", error);
        }
    }
});

updateBlockedWebsites();
setInterval(updateBlockedWebsites, 5000);
