document.querySelectorAll(".message").forEach((message) => {
    setTimeout(() => {
        message.style.opacity = "0";
    }, 2500);
});
