(function () {
  var root = document.documentElement;
  var toggle = document.getElementById("theme-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var next = root.dataset.theme === "dark" ? "light" : "dark";
      if (next === "light") {
        delete root.dataset.theme;
      } else {
        root.dataset.theme = next;
      }
      try {
        localStorage.setItem("theme", next);
      } catch (e) {}
    });
  }

  document.querySelectorAll(".post-content pre").forEach(function (pre) {
    var parent = pre.parentElement;
    var host;
    if (parent && parent.classList.contains("highlight")) {
      host = parent;
    } else {
      host = document.createElement("div");
      host.className = "highlight";
      pre.parentNode.insertBefore(host, pre);
      host.appendChild(pre);
    }
    host.classList.add("code-host");

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "copy-btn";
    btn.textContent = "复制";
    btn.addEventListener("click", function () {
      navigator.clipboard.writeText(pre.innerText).then(function () {
        btn.textContent = "已复制";
        btn.classList.add("copied");
        setTimeout(function () {
          btn.textContent = "复制";
          btn.classList.remove("copied");
        }, 1500);
      });
    });
    host.appendChild(btn);
  });
})();
