
function checkWebsite() {
    if (!chrome?.storage?.local) return;

    chrome.storage.local.get(["blockedWebsites"], function (result) {
        if (chrome.runtime.lastError) {
            return;
        }

        const blockedWebsites = result.blockedWebsites || [];
        const currentWebsite = window.location.hostname.toLowerCase();

        const existingBlock = document.getElementById("study-shield-block");

        const shouldBlock = blockedWebsites.some(website => {
            const blockedDomain = website
                .toLowerCase()
                .replace(/^https?:\/\//, "")
                .replace(/^www\./, "")
                .split("/")[0]
                .split(":")[0];

            return currentWebsite === blockedDomain ||
                   currentWebsite.endsWith("." + blockedDomain);
        });

        if (shouldBlock && !existingBlock) {
            const blockScreen = document.createElement("div");
            blockScreen.id = "study-shield-block";

            blockScreen.style.cssText = `
                position: fixed;
                inset: 0;
                width: 100%;
                height: 100%;
                z-index: 2147483647;
                background: #100B1F;
                color: #F5F3FF;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: Arial, sans-serif;
                text-align: center;
            `;

            blockScreen.innerHTML = `
                <div style="
                    background:#1A1329;
                    padding:45px;
                    border-radius:20px;
                    border:1px solid #302445;
                    max-width:450px;
                    margin:20px;
                    box-shadow:0 15px 50px rgba(167,139,250,0.15);
                ">
                    <div style="font-size:55px;">🛡️</div>
                    <h1 style="color:#A78BFA;margin:15px 0;">Study Shield</h1>
                    <h2>Website Blocked</h2>
                    <p style="color:#B8B1C9;margin-top:15px;">
                        This website is blocked during your focus session.
                    </p>
                    <p style="color:#F472B6;margin-top:20px;font-weight:bold;">
                        🎯 Stay focused. Keep going!
                    </p>
                </div>
            `;

            document.documentElement.appendChild(blockScreen);
            chrome.runtime.sendMessage({
    type: "STUDY_SHIELD_BLOCKED",
    website: window.location.hostname
});
        }

        if (!shouldBlock && existingBlock) {
            existingBlock.remove();
        }
    });
}

// Check immediately when the page loads
checkWebsite();

// Recheck immediately whenever the blocklist changes
chrome.storage.onChanged.addListener((changes, areaName) => {
    if (areaName === "local" && changes.blockedWebsites) {
        checkWebsite();
    }
});

// Backup check every 5 seconds
setInterval(checkWebsite, 5000);
