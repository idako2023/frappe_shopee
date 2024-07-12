// Assuming you have redirect_handler.js or similar
document.addEventListener("DOMContentLoaded", function() {
    const urlParams = new URLSearchParams(window.location.search);
    const authCode = urlParams.get('code');
    const mainAccountId = urlParams.get('main_account_id'); // If needed

    if (authCode) {
        fetch(`/api/method/shopee.api.auth.handle_auth_code`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Frappe-CSRF-Token': frappe.csrf_token
            },
            body: JSON.stringify({ auth_code: authCode, main_account_id: mainAccountId })
        }).then(response => response.json())
          .then(data => {
              console.log('Token fetched', data);
              // Handle further navigation or display success message
          }).catch(error => {
              console.error('Error fetching token', error);
          });
    }
});
