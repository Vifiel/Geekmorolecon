function openRegForm() {
  document.getElementById("regForm").style.display = "block";
}

function closeRegForm() {
  document.getElementById("regForm").style.display = "none";
}

function openEnterForm() {
  document.getElementById("enterForm").style.display = "block";
}

function closeEnterForm() {
  document.getElementById("enterForm").style.display = "none";
}

document.addEventListener("DOMContentLoaded", function () {

    document.getElementById("EnterForm").addEventListener("submit", function (e) {
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
            closeEnterForm()
        } else {
            document.getElementById("error").textContent = "Пользователь не найден.";
        }
        })
    });
});
