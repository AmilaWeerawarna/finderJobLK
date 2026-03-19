// static/js/dashboard.js

document.addEventListener("DOMContentLoaded", function () {

    
// 1. Tab Switching Logic (වෙනස් කළ කොටස)
    const tabButtons = document.querySelectorAll(".dashboard-sidebar .tab-btn[data-target]");
    const tabContents = document.querySelectorAll(".dashboard-content .tab-content");

    tabButtons.forEach(button => {
        button.addEventListener("click", () => {
            // Remove active class from all buttons and tabs
            tabButtons.forEach(btn => btn.classList.remove("active"));
            tabContents.forEach(content => content.classList.remove("active"));

            // Add active class to the clicked button
            button.classList.add("active");

            // Show the target tab content
            const targetId = button.getAttribute("data-target");
            const targetTab = document.getElementById(targetId);
            if (targetTab) {
                targetTab.classList.add("active");
            }
        });
    });

    // 2. Image Upload Preview Logic (Job Image)
    const imageInput = document.getElementById("job_image");
    const imagePreview = document.getElementById("imagePreview");
    const imageLabel = document.getElementById("imageLabel");

    if (imageInput) {
        imageInput.addEventListener("change", function(event) {
            const file = event.target.files[0];
            
            if (file) {
                // FileReader වෙනුවට URL.createObjectURL භාවිතා කිරීම (Lag එක නැති කරයි)
                imagePreview.src = URL.createObjectURL(file);
                imagePreview.style.display = "block"; // පින්තූරය පෙන්වයි
                imageLabel.style.display = "none";    // කැමරා අයිකනය සඟවයි
            } else {
                imagePreview.src = "";
                imagePreview.style.display = "none";
                imageLabel.style.display = "flex";
            }
        });

        // පින්තූරය උඩ Click කළ විටත් අලුත් පින්තූරයක් තේරීමට අවස්ථාව දීම
        if (imagePreview) {
            imagePreview.addEventListener("click", function() {
                imageInput.click();
            });
            imagePreview.style.cursor = "pointer"; // Click කළ හැකි බව පෙන්වීමට
        }
    }
}); // DOMContentLoaded අවසානය


// --- Custom Delete Modal Logic ---
function openDeleteModal(draftId) {
    const modal = document.getElementById("deleteModal");
    const confirmBtn = document.getElementById("confirmDeleteBtn");
    confirmBtn.href = "/employer/delete-draft/" + draftId;
    modal.style.display = "flex";
}

function closeDeleteModal() {
    document.getElementById("deleteModal").style.display = "none";
}

window.onclick = function(event) {
    const modal = document.getElementById("deleteModal");
    if (event.target === modal) {
        closeDeleteModal();
    }
}


// --- Profile Settings Image Preview Logic ---
document.addEventListener("DOMContentLoaded", function () {
    const profileImageInput = document.getElementById("profile_image_upload");
    const profileImagePreview = document.getElementById("profileImagePreview");
    const defaultIcon = document.querySelector(".default-icon"); 

    if (profileImageInput) {
        profileImageInput.addEventListener("change", function(event) {
            const file = event.target.files[0];
            
            if (file) {
                // Lag එක නැති කිරීමට URL.createObjectURL යොදා ඇත
                profileImagePreview.src = URL.createObjectURL(file);
                profileImagePreview.style.display = "block"; 
                if (defaultIcon) {
                    defaultIcon.style.display = "none";
                }
            }
        });
    }
});


// 🟢 Active Jobs වල Delete Popup එක පෙන්වීම
function openActiveJobDeleteModal(jobId) {
    const modal = document.getElementById("deleteModal");
    const confirmBtn = document.getElementById("confirmDeleteBtn");
    
    // අදාළ Route එකට Job ID එක යොමු කිරීම
    confirmBtn.href = "/employer/delete-active-job/" + jobId;
    modal.style.display = "flex";
}

document.addEventListener("DOMContentLoaded", function () {
    // 🟢 Real-time Job Search Logic (Cards සඳහා)
    const searchInput = document.getElementById("jobSearchInput");
    
    if (searchInput) {
        searchInput.addEventListener("keyup", function () {
            let filterText = this.value.toLowerCase();
            let cards = document.querySelectorAll("#activeJobsContainer .job-card");
            let visibleCount = 0;

            cards.forEach(card => {
                let titleElement = card.querySelector(".card-title");
                
                if (titleElement) {
                    let titleText = titleElement.textContent || titleElement.innerText;
                    
                    if (titleText.toLowerCase().indexOf(filterText) > -1) {
                        card.style.display = "flex"; // Card එක පෙන්වයි
                        visibleCount++;
                    } else {
                        card.style.display = "none"; // Card එක සඟවයි
                    }
                }
            });

            // කිසිම රිසල්ට් එකක් නැත්නම් පණිවිඩය පෙන්වීම
            let noJobsMessage = document.getElementById("noJobsMessage");
            if (noJobsMessage) {
                if (visibleCount === 0 && cards.length > 0) {
                    noJobsMessage.style.display = "block";
                    noJobsMessage.innerHTML = `<i class="fas fa-search" style="font-size: 30px; color: var(--dp-24); margin-bottom: 10px; display: block;"></i>No active jobs matching "${this.value}" found.`;
                } else {
                    noJobsMessage.style.display = "none";
                }
            }
        });
    }
});