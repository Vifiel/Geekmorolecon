document.addEventListener("DOMContentLoaded", function () {

  const registrationBtn = document.getElementById("Registration");
  const regCloseBtn = document.getElementById("RegClose");
  const RegForm = document.getElementById("RegForm");
  const regForm = document.getElementById("regForm");

  const enterBtn = document.getElementById("Enter");
  const EnterForm = document.getElementById("EnterForm");
  const enterForm = document.getElementById("enterForm");
  const enterCloseBtn = document.getElementById("EnterClose");

  const createSectionBtn = document.getElementById("createSection");
  const CreateSectionForm = document.getElementById("CreateSectionForm");
  const createSectionForm = document.getElementById("createSectionForm");
  const createSectionFormClose = document.getElementById("CreateSectionFormClose");

  const userNotFoundError = document.getElementById("NotInDatabase");
  const unmatchedPasswordsError = document.getElementById("UnmatchedPasswords");
  const alreadyRegistredError = document.getElementById("InDatabase");

  const exitBtn = document.getElementById("exitBtn");

  document.querySelectorAll('.dropdown-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      const dropdownContent = btn.parentElement.querySelector('.dropdown-content');
      if (dropdownContent) {
        dropdownContent.style.display = dropdownContent.style.display === "block" ? "none" : "block";
      }
    });
  });

  const toSectionsBtn = document.getElementById("toSectionsBtn");
  if (toSectionsBtn) {
    toSectionsBtn.addEventListener("click", function () {
      const sections = document.getElementById("sections");
      if (sections) {
        sections.scrollIntoView({ behavior: "smooth" });
      }
    });
  }

  if (createSectionBtn && CreateSectionForm) {
    createSectionBtn.addEventListener("click", function () {
      CreateSectionForm.style.display = "block";
      if (EnterForm) EnterForm.style.display = "none";
      if (regForm) RegForm.style.display = "none";
    });
  }

  if (createSectionFormClose){
    createSectionFormClose.addEventListener("click", function () {
      CreateSectionForm.style.display = "none";
      createSectionForm.reset();
    });
  }


  if (registrationBtn && RegForm) {
    registrationBtn.addEventListener("click", function () {
      RegForm.style.display = "block";
      if (EnterForm) EnterForm.style.display = "none";
      if (CreateSectionForm) CreateSectionForm.style.display = "none";
    });
  }

  if (regCloseBtn){
    regCloseBtn.addEventListener("click", function () {
      RegForm.style.display = "none";
      alreadyRegistredError.textContent = "";
      regForm.reset();
    });
  }

  if (enterBtn && EnterForm) {
    enterBtn.addEventListener("click", function () {
      console.log("нажат вход")
      EnterForm.style.display = "block";
      if (RegForm) RegForm.style.display = "none";
      if (CreateSectionForm) CreateSectionForm.style.display = "none"
    });
  }

  if (enterCloseBtn){
    enterCloseBtn.addEventListener("click", function () {
      EnterForm.style.display = "none";
      unmatchedPasswordsError.textContent = "";
      userNotFoundError.textContent = "";
      enterForm.reset();
    });
  }
  
  exitBtn.addEventListener("click", function(){
    registrationBtn.style.display = "block";
    enterBtn.style.display = "block";
    exitBtn.style.display = "none";
  })

  if (enterForm) {
      enterForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const email = document.getElementById("email");
        const password = document.getElementById("password");

        fetch("/enter", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email: email.value, password: password.value })
        })
        .then(response => response.json())
        .then(data => {
        if (!data.exists) {
            email.value = "";
            userNotFoundError.textContent = "Пользователь не найден";
        } else if (!data.passMatch){
            document.getElementById("UnmatchedPasswords").textContent = "Неверный пароль";
        } else {
            enterForm.reset()
            registrationBtn.style.display = "none";
            enterBtn.style.display = "none";
            exitBtn.style.display = "block";
            EnterForm.style.display = "none";
        }
        })
    });
  }

  if (regForm) {
      regForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const email = document.getElementById("regEmail");
        const password = document.getElementById("regPassword");
        const name = document.getElementById("regName");

        fetch("/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email: email.value, password: password.value, name: name.value })
        })
        .then(response => response.json())
        .then(data => {
        if (data.exists) {
            email.value = "";
            alreadyRegistredError.textContent = "Пользователь уже зарегистрирован";
        } else {
            regForm.reset()
            RegForm.style.display = "none";
        }
        })
    });
  }
});

