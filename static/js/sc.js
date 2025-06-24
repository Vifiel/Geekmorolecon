document.addEventListener("DOMContentLoaded", function () {

  const registrationBtn = document.getElementById("Registration");
  const regCloseBtn = document.getElementById("RegClose");
  const regForm = document.getElementById("RegForm");

  const enterBtn = document.getElementById("Enter");
  const EnterForm = document.getElementById("EnterForm");
  const enterForm = document.getElementById("enterForm");
  const enterCloseBtn = document.getElementById("EnterClose");

  document.querySelectorAll('.dropdown-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      const dropdownContent = btn.parentElement.querySelector('.dropdown-content');
      if (dropdownContent) {
        dropdownContent.style.display = dropdownContent.style.display === "block" ? "none" : "block";
      }
    });
  });


  if (registrationBtn && regForm) {
    registrationBtn.addEventListener("click", function () {
      regForm.style.display = "block";
      if (EnterForm) EnterForm.style.display = "none";
    });
  }

  if (regCloseBtn){
    regCloseBtn.addEventListener("click", function () {
      regForm.style.display = "none";
    });
  }

  if (enterBtn && EnterForm) {
    enterBtn.addEventListener("click", function () {
      EnterForm.style.display = "block";
      if (regForm) regForm.style.display = "none";
    });
  }

  if (enterCloseBtn){
    enterCloseBtn.addEventListener("click", function () {
      enterForm.style.display = "none";
    });
  }

  if (enterForm) {
      enterForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        fetch("/enter", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email: email, password: password })
        })
        .then(response => response.json())
        .then(data => {
        if (!data.exists) {
            document.getElementById("NotInDatabase").textContent = "Пользователь не найден.";
        } else if (!data.passMatch){
            document.getElementById("UnmatchedPasswords").textContent = "Неверный пароль";
        } else {
            EnterForm.style.display = "none";
        }
        })
      console.log("Форма отправлена!");
    });
  }
});

