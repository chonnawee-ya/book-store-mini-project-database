/**
 * E-Book Store Mini Project - Minimal UI & Interactive Utilities (2026)
 */

document.addEventListener("DOMContentLoaded", () => {
    // -------------------------------------------------------------------------
    // 1. Theme Toggle (Light / Dark Mode) with localStorage persistence
    // -------------------------------------------------------------------------
    const themeToggleBtn = document.getElementById("theme-toggle-btn");
    
    function getCurrentTheme() {
        return document.documentElement.getAttribute("data-theme") || "light";
    }

    function setTheme(newTheme) {
        document.documentElement.setAttribute("data-theme", newTheme);
        try {
            localStorage.setItem("theme", newTheme);
        } catch (e) {}
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", () => {
            const currentTheme = getCurrentTheme();
            const nextTheme = currentTheme === "dark" ? "light" : "dark";
            setTheme(nextTheme);
        });
    }

    // -------------------------------------------------------------------------
    // 2. Mobile Navigation Drawer & Backdrop Toggle
    // -------------------------------------------------------------------------
    const mobileMenuBtn = document.getElementById("mobile-menu-btn");
    const navDrawer = document.getElementById("nav-drawer");
    const navOverlay = document.getElementById("nav-overlay");

    function openMobileMenu() {
        if (navDrawer) navDrawer.classList.add("open");
        if (navOverlay) navOverlay.classList.add("active");
        document.body.style.overflow = "hidden";
    }

    function closeMobileMenu() {
        if (navDrawer) navDrawer.classList.remove("open");
        if (navOverlay) navOverlay.classList.remove("active");
        document.body.style.overflow = "";
    }

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener("click", () => {
            if (navDrawer && navDrawer.classList.contains("open")) {
                closeMobileMenu();
            } else {
                openMobileMenu();
            }
        });
    }

    if (navOverlay) {
        navOverlay.addEventListener("click", closeMobileMenu);
    }

    // Close mobile drawer when clicking any nav link
    if (navDrawer) {
        const navLinks = navDrawer.querySelectorAll(".nav-link");
        navLinks.forEach(link => {
            link.addEventListener("click", closeMobileMenu);
        });
    }

    // -------------------------------------------------------------------------
    // 3. Accordion for SQL Explanations
    // -------------------------------------------------------------------------
    const accordions = document.querySelectorAll(".sql-accordion");
    accordions.forEach(acc => {
        const header = acc.querySelector(".sql-header");
        const body = acc.querySelector(".sql-body");
        if (header && body) {
            header.addEventListener("click", () => {
                const isHidden = body.style.display === "none";
                body.style.display = isHidden ? "block" : "none";
                const arrow = header.querySelector(".accordion-arrow");
                if (arrow) {
                    arrow.textContent = isHidden ? "▲ ซ่อนคำอธิบาย SQL" : "▼ ดูคำอธิบายคำสั่ง SQL";
                }
            });
        }
    });

    // -------------------------------------------------------------------------
    // 4. Interactive SQL Query Runner in Database Explorer
    // -------------------------------------------------------------------------
    const runBtn = document.getElementById("run-query-btn");
    const queryInput = document.getElementById("custom-sql-input");
    const queryResultsWrap = document.getElementById("query-results-container");

    if (runBtn && queryInput && queryResultsWrap) {
        runBtn.addEventListener("click", async () => {
            const sql = queryInput.value.trim();
            if (!sql) return;

            runBtn.disabled = true;
            runBtn.textContent = "กำลังรัน...";
            queryResultsWrap.innerHTML = `<div style="padding: 1.25rem; text-align: center; color: var(--text-muted);">กำลังดำเนินการคิวรี...</div>`;

            try {
                const res = await fetch("/api/query-runner", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ sql })
                });
                const data = await res.json();

                if (!data.success) {
                    queryResultsWrap.innerHTML = `
                        <div class="alert alert-danger" style="margin: 0.75rem 0;">
                            <strong>ข้อผิดพลาดของ SQL:</strong> ${data.error}
                        </div>
                    `;
                } else if (data.data.length === 0) {
                    queryResultsWrap.innerHTML = `
                        <div class="alert alert-info" style="margin: 0.75rem 0;">
                            ไม่พบข้อมูลจากเงื่อนไข Query (0 แถว)
                        </div>
                    `;
                } else {
                    let tableHtml = `
                        <div style="margin: 0.75rem 0; font-size: 0.8rem; color: var(--status-success-text); font-weight: 500;">
                            ✓ ประมวลผลสำเร็จ: พบทั้งหมด ${data.row_count} แถว
                        </div>
                        <div class="table-responsive">
                            <table class="custom-table">
                                <thead>
                                    <tr>
                                        ${data.columns.map(c => `<th>${c}</th>`).join("")}
                                    </tr>
                                </thead>
                                <tbody>
                                    ${data.data.map(row => `
                                        <tr>
                                            ${data.columns.map(c => `<td>${row[c] !== null ? row[c] : '<em style="color:var(--text-muted);">NULL</em>'}</td>`).join("")}
                                        </tr>
                                    `).join("")}
                                </tbody>
                            </table>
                        </div>
                    `;
                    queryResultsWrap.innerHTML = tableHtml;
                }
            } catch (err) {
                queryResultsWrap.innerHTML = `
                    <div class="alert alert-danger" style="margin: 0.75rem 0;">
                        เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์: ${err.message}
                    </div>
                `;
            } finally {
                runBtn.disabled = false;
                runBtn.textContent = "รันคำสั่ง SQL";
            }
        });
    }

    // Preset Query buttons in Database Explorer
    const presetBtns = document.querySelectorAll(".preset-query-btn");
    presetBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const query = btn.getAttribute("data-sql");
            if (queryInput && query) {
                queryInput.value = query.trim();
                if (runBtn) runBtn.click();
            }
        });
    });

    // -------------------------------------------------------------------------
    // 5. Modal Handler for Slip Preview
    // -------------------------------------------------------------------------
    window.previewSlip = function(url, orderId) {
        const modal = document.getElementById("slip-modal");
        const img = document.getElementById("modal-slip-img");
        const title = document.getElementById("modal-slip-title");
        if (modal && img && title) {
            img.src = url;
            title.textContent = `สลิปจำลองคำสั่งซื้อ #${orderId}`;
            modal.style.display = "flex";
        }
    };

    window.closeSlipModal = function() {
        const modal = document.getElementById("slip-modal");
        if (modal) modal.style.display = "none";
    };
});
