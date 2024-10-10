// Simple script for navigation interactions
document.addEventListener("DOMContentLoaded", function() {
    // Highlight the active navigation link
    const navLinks = document.querySelectorAll("nav ul li a");
    navLinks.forEach(link => {
        if (link.href === window.location.href) {
            link.style.backgroundColor = "#34495e";
        }
    });

    // // Example functionality: alert when login button is clicked
    // const loginLink = document.querySelector("a[href*='login']");
    // if (loginLink) {
    //     loginLink.addEventListener('click', function(event) {
    //         event.preventDefault();
    //         // alert("Login functionality is not yet implemented.");
    //     });
    // }
});
