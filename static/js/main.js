(() => {
// ----------------------------
  // Score ring animation (data-score -> ring + text)
  // Works even if some browsers don't animate @property
  // ----------------------------
  function clamp(n, min, max) { return Math.max(min, Math.min(max, n)); }

  function animateRingTo(ringEl, score) {
    // Set to 0 first so it animates from empty
    ringEl.style.setProperty("--p", 0);

    // Use rAF to ensure browser paints 0 before moving to score
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        ringEl.style.setProperty("--p", score);
      });
    });

    // Fallback for browsers that don't animate CSS custom properties:
    // do a small JS animation only if we detect no support for @property
    // (Safari older versions)
    const supportsProperty = CSS && CSS.registerProperty;
    if (!supportsProperty) {
      let current = 0;
      const duration = 900;
      const start = performance.now();

      function step(t) {
        const p = clamp((t - start) / duration, 0, 1);
        current = Math.round(score * p);
        ringEl.style.setProperty("--p", current);
        if (p < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    }
  }

  function animateJobScores() {
    document.querySelectorAll(".job-card-light").forEach((card) => {
      const ringEl = card.querySelector(".score-circle-light");
      const textEl = card.querySelector(".score-text");

      // 1. පැරණි කේතයේ තිබූ parseInt වෙනුවට parseFloat භාවිතා කරන්න.
      // එවිට දශම සංඛ්‍යා (Decimals) ඉවත් නොවී සුරැකේ.
      let score = parseFloat(card.getAttribute("data-score") || "0");

      score = clamp(isNaN(score) ? 0 : score, 0, 100);

      // 2. අගය පෙන්වන ස්ථානය (Text Display)
      if (textEl) {
          // ඔබට දශම ස්ථාන 1ක් පමණක් පෙන්වීමට අවශ්‍ය නම් .toFixed(1) භාවිතා කරන්න (උදා: 85.5%)
          // නැතහොත් දශම ස්ථාන 2ක් සඳහා .toFixed(2) භාවිතා කරන්න (උදා: 85.52%)
          // තිබෙන ආකාරයෙන්ම පෙන්වීමට අවශ්‍ය නම් පහත පේළිය භාවිතා කරන්න:
          textEl.textContent = `${score}%`; 
          
          // උදාහරණයක් ලෙස දශම ස්ථාන 1කට (One decimal place) සීමා කිරීමට නම්:
          // textEl.textContent = `${score.toFixed(1)}%`;
      }

      if (ringEl) animateRingTo(ringEl, score);
    });
  }

  window.addEventListener("load", animateJobScores);
})();

document.addEventListener("DOMContentLoaded", function () {
  // 1. බොත්තම් එබූ විට Loading පෙන්වීමේ නිවැරදි කේතය (Safe Form Submit)
  document.querySelectorAll("form").forEach(form => {
    form.addEventListener("submit", function (e) {
      const btn = form.querySelector("button[type='submit']");
      if (!btn) return;

      // Browser එකට Form එක submit කරන්න පොඩි වෙලාවක් (මිලි තත්පර 10ක්) දීලා 
      // ඊට පස්සේ බොත්තමේ අකුරු වෙනස් කරනවා. (මෙය Submit වීම නතර වීම වළක්වයි)
      setTimeout(() => {
        if (!btn.classList.contains("btn-loading")) {
          btn.dataset.originalText = btn.innerHTML;
          btn.classList.add("btn-loading");
          
          // Match බොත්තමට වෙනම ලස්සන අකුරු පෙළක් 
          if(btn.id === 'matchBtn') {
              btn.innerHTML = '<span class="btn-spinner"></span> Analyzing CV...';
          } else {
              btn.innerHTML = '<span class="btn-spinner"></span>'+btn.innerHTML;
          }
        }
      }, 10);
    });
  });

  // 2. Profile Menu Dropdown එක සඳහා කේතය
  const profileTrigger = document.getElementById("profileTrigger");
  const profileDropdown = document.getElementById("profileDropdown");

  if (profileTrigger && profileDropdown) {
      profileTrigger.addEventListener("click", (e) => {
          e.stopPropagation();
          profileDropdown.classList.toggle("show");
      });

      // වෙනත් තැනක් එබූ විට මෙනුව වැසීම
      document.addEventListener("click", () => {
          profileDropdown.classList.remove("show");
      });
  }
});




// Fade-in animation
      document.querySelectorAll('.hero > *, .site-footer').forEach((el, i) => {
        el.style.opacity = 0;
        el.style.transform = 'translateY(15px)';
        setTimeout(() => {
          el.style.transition = '0.8s ease';
          el.style.opacity = 1;
          el.style.transform = 'translateY(0)';
        }, i * 150);
      });

      // Change Header Background on Scroll
      const header = document.querySelector('header');

      window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
          header.classList.add('scrolled');
        } else {
          header.classList.remove('scrolled');
        }
      });

      // Add .register-card to the animation list
      document.querySelectorAll('.hero > *, .login-card, .register-card, .site-footer').forEach((el, i) => {
        // Existing animation logic stays the same...
      });

      // Refined Toggle logic for the theme
      function toggleEmployerFields() {
        const role = document.getElementById("role").value;
        const employerFields = document.getElementById("employerFields");
        
        if (role === "employer") {
          employerFields.style.display = "flex";
          // Small timeout to allow browser to register display:flex before animating opacity
          setTimeout(() => { employerFields.style.opacity = "1"; }, 10);
        } else {
          employerFields.style.display = "none";
        }
      }

      /* --- Update the Fade-in animation list in your existing script.js --- */
      document.querySelectorAll('.hero > *, .login-card, .register-card, .forgot-card, .site-footer').forEach((el, i) => {
        el.style.opacity = 0;
        el.style.transform = 'translateY(15px)';
        setTimeout(() => {
          el.style.transition = '0.8s ease';
          el.style.opacity = 1;
          el.style.transform = 'translateY(0)';
        }, i * 150);
      });

      /* The scroll-based header background and mobile menu logic 
        added previously will automatically work here. */


      /* --- Update the selector in your existing fade-in logic --- */
      document.querySelectorAll('.hero > *, .login-card, .register-card, .forgot-card, .reset-card, .site-footer').forEach((el, i) => {
        el.style.opacity = 0;
        el.style.transform = 'translateY(15px)';
        setTimeout(() => {
          el.style.transition = '0.8s ease';
          el.style.opacity = 1;
          el.style.transform = 'translateY(0)';
        }, i * 150);
      });

      /* The scroll logic and mobile menu toggle will work automatically */


      // Mobile Menu Toggle Logic
      const menuToggle = document.getElementById('menuToggle');
      const navMenu = document.getElementById('navMenu');

      menuToggle.addEventListener('click', () => {
        menuToggle.classList.toggle('active');
        navMenu.classList.toggle('active');
      });

      // Close menu when clicking a link
      document.querySelectorAll('nav span').forEach(link => {
        link.addEventListener('click', () => {
          menuToggle.classList.remove('active');
          navMenu.classList.remove('active');
        });
      });

      // ==========================================
      // NEW PDF UPLOAD LOGIC (Image-like UI)
      // ==========================================
      const pdfUpload = document.getElementById('pdfUpload');
      const uploadLabel = document.getElementById('uploadLabel');
      const fileSelectedBox = document.getElementById('fileSelectedBox');
      const pdfFileName = document.querySelector('#pdfFileName span');
      const removePdfBtn = document.getElementById('removePdfBtn');
      const dropZone = document.querySelector('.upload-card');

      if (pdfUpload) {
        // File එකක් තේරූ විට
        pdfUpload.addEventListener('change', () => {
          if (pdfUpload.files.length > 0) {
            pdfFileName.textContent = pdfUpload.files[0].name;
            uploadLabel.style.display = 'none'; // රතු බොත්තම සඟවයි
            fileSelectedBox.style.display = 'block'; // Submit බොත්තම පෙන්වයි
            dropZone.style.borderColor = 'var(--accent-color)'; // Border එකේ පාට වෙනස් කරයි
          }
        });

        // Cancel බොත්තම එබූ විට
        removePdfBtn.addEventListener('click', () => {
          pdfUpload.value = ''; // File එක clear කරයි
          uploadLabel.style.display = 'inline-block'; // රතු බොත්තම ආපසු පෙන්වයි
          fileSelectedBox.style.display = 'none'; // Submit බොත්තම සඟවයි
          dropZone.style.borderColor = 'var(--dp-24)'; // Border පාට සාමාන්‍ය තත්වයට පත් කරයි
        });

        // Drag and Drop (ගෙනැවිත් දැමීම) සඳහා
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = '#ff3b30'; // Drag කරන විට රතු පාට වේ
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.style.borderColor = 'var(--dp-24)';
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            if (e.dataTransfer.files.length > 0) {
                const file = e.dataTransfer.files[0];
                if(file.type === "application/pdf") {
                    pdfUpload.files = e.dataTransfer.files;
                    // change event එක force කර trigger කිරීම
                    const event = new Event('change');
                    pdfUpload.dispatchEvent(event);
                } else {
                    alert("Please drop a valid PDF file.");
                    dropZone.style.borderColor = 'var(--dp-24)';
                }
            }
        });
      }

      document.addEventListener("DOMContentLoaded", function () {
          // 🟢 Toast Notifications තත්පර 5කින් සැඟවීම
          const toasts = document.querySelectorAll('.toast-message');
          
          toasts.forEach(toast => {
              setTimeout(() => {
                  // මැකී යන Animation එක එක් කිරීම
                  toast.classList.add('hiding');
                  
                  // Animation එක ඉවර වූ පසු HTML එකෙන් අයින් කිරීම
                  setTimeout(() => {
                      toast.remove();
                  }, 500); // Transition එකට යන කාලය (0.5s)
                  
              }, 3000); // තත්පර 3 (3000ms) කින් මෙය ක්‍රියාත්මක වේ
          });
      });