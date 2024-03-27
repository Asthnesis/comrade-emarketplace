function myFunction() {
    document.getElementById("myDropdown").classList.toggle("show");
  }
  
  // Close the dropdown menu if the user clicks outside of it
  window.onclick = function(event) {
    if (!event.target.matches('.dropdown')) {
      var dropdowns = document.getElementsByClassName("dropdown-content");
      var i;
      for (i = 0; i < dropdowns.length; i++) {
        var openDropdown = dropdowns[i];
        if (openDropdown.classList.contains('show')) {
          openDropdown.classList.remove('show');
        }
      }
    }
  }

  // Get the current URL path
const path = window.location.pathname.split('/').filter(element => element !== '');

// Create a function to generate the breadcrumb
function generateBreadcrumb(path) {
  const breadcrumbContainer = document.getElementById('breadcrumb');
  let breadcrumbHTML = `<li><a href="/">Home</a></li>`; // Start with the Home link

  // Build the breadcrumb HTML
  path.forEach((segment, index) => {
    const url = `/${path.slice(0, index + 1).join('/')}`;
    breadcrumbHTML += `<li><a href="${url}">${segment}</a></li>`;
  });

  // Set the breadcrumb HTML
  breadcrumbContainer.innerHTML = breadcrumbHTML;
}

// Call the function on page load
generateBreadcrumb(path);

function toggleAccountInfo() {
  var form = document.getElementById("account-info-form");
  if (form.style.display === "none") {
      form.style.display = "block";
  } else {
      form.style.display = "none";
  }
}

const togglePassword = document.getElementById('togglePassword');
const password = document.getElementById('password');

togglePassword.addEventListener('click', function () {
    // Toggle between password visibility
    if (password.type === "password") {
        password.type = "text";
        this.classList.remove('fa-eye'); // Change icon to eye-slash (visible)
        this.classList.add('fa-eye-slash');
    } else {
        password.type = "password";
        this.classList.remove('fa-eye-slash'); // Change icon to eye (hidden)
        this.classList.add('fa-eye');
    }
});
function validateForm() {
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirm-password').value;

  // Email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
      alert('Please enter a valid email address.');
      return false;
  }

  // Password length validation
  if (password.length < 8) {
      alert('Password must be at least 8 characters long.');
      return false;
  }

  // Password confirmation validation
  if (password !== confirmPassword) {
      alert('Passwords do not match.');
      return false;
  }

  // Add more password validation rules as needed

  return true;
}
function showSection(sectionName) {
  // Hide all sections
  document.querySelectorAll('.profile-account-info, .profile-change-password, .profile-logout').forEach(function(el) {
      el.classList.remove('show');
  });

  // Show only the selected section
  document.querySelector('.' + sectionName).classList.add('show');
}

