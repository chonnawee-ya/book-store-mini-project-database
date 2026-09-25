/**
 * E-Book Store Mini Project - Interactive JavaScript Utilities
 */

document.addEventListener("DOMContentLoaded", () => {
    // 1. Accordion for SQL Explanations
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

    // 2. Interactive SQL Query Runner in Database Explorer
    const runBtn = document.getElementById("run-query-btn");
    const queryInput = document.getElementById("custom-sql-input");
    const queryResultsWrap = document.getElementById("query-results-container");

    if (runBtn && queryInput && queryResultsWrap) {
        runBtn.addEventListener("click", async () => {
            const sql = queryInput.value.trim();
            if (!sql) return;

            runBtn.disabled = true;
            runBtn.textContent = "กำลังประมวลผล...";
            queryResultsWrap.innerHTML = `<div style="padding: 1.5rem; text-align: center; color: #94a3b8;">กำลังดำเนินการ Query...</div>`;

            try {
                const res = await fetch("/api/query-runner", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ sql })
                });
                const data = await res.json();

                if (!data.success) {
                    queryResultsWrap.innerHTML = `
                        <div class="alert alert-danger" style="margin: 1rem 0;">
                            <strong>ข้อผิดพลาดของ SQL:</strong> ${data.error}
                        </div>
                    `;
                } else if (data.data.length === 0) {
                    queryResultsWrap.innerHTML = `
                        <div class="alert alert-info" style="margin: 1rem 0;">
                            ไม่พบข้อมูลจากเงื่อนไข Query (0 แถว)
                        </div>
                    `;
                } else {
                    let tableHtml = `
                        <div style="margin: 1rem 0; font-size: 0.85rem; color: #34d399;">
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
                                            ${data.columns.map(c => `<td>${row[c] !== null ? row[c] : '<em style="color:#64748b;">NULL</em>'}</td>`).join("")}
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
                    <div class="alert alert-danger" style="margin: 1rem 0;">
                        เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์: ${err.message}
                    </div>
                `;
            } finally {
                runBtn.disabled = false;
                runBtn.textContent = "รันคำสั่ง SQL";
            }
        });
    }

    // 3. Preset Query buttons in Database Explorer
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

    // 4. Modal handler for slip preview
    window.previewSlip = function(url, orderId) {
        const modal = document.getElementById("slip-modal");
        const img = document.getElementById("modal-slip-img");
        const title = document.getElementById("modal-slip-title");
        if (modal && img && title) {
            img.src = url;
            title.textContent = `สลิปจำลองสำหรับคำสั่งซื้อ #${orderId}`;
            modal.style.display = "flex";
        }
    };

    window.closeSlipModal = function() {
        const modal = document.getElementById("slip-modal");
        if (modal) modal.style.display = "none";
    };
});
