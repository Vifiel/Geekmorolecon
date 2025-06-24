document.addEventListener("DOMContentLoaded", function () {
  // Кнопка "Регистрация" — открывает форму
  const registrationBtn = document.getElementById("Registration");
  const enterBtn = document.getElementById("Enter");
  const regForm = document.getElementById("RegForm");
  const EnterForm = document.getElementById("EnterForm");
  const enterForm = document.getElementById("enterForm");
  const regCloseBtn = document.getElementById("RegClose");
  const enterCloseBtn = document.getElementById("EnterClose");

  if (registrationBtn && regForm) {
    registrationBtn.addEventListener("click", function () {
      regForm.style.display = "block";
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
        if (data.exists) {
            EnterForm.style.display = "none";
        } else {
            document.getElementById("error").textContent = "Пользователь не найден.";
        }
        })
      console.log("Форма отправлена!");
    });
  }
});

