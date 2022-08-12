
function checkForm() {
    if (document.getElementById('username')).value == '' or document.getElementById('password').value == '') {
        alert ('Заполните все поля');
        return false;
        }
    else {
        return true
        }
    }



let button = document.getElementById('post-btn');

button.addEventListener('click', async _ => {

    if checkForm(): {
        les username = document.getElementById('username').value;
    let password = document.getElementById('password').value;
    try {
    let response = await fetch('/authorization/sign_in', {
          method: 'POST', // *GET, POST, PUT, DELETE, etc.
          mode: 'cors', // no-cors, *cors, same-origin
          cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
          credentials: 'same-origin', // include, *same-origin, omit
          headers: {
          'Content-Type': 'application/json'
            // 'Content-Type': 'application/x-www-form-urlencoded',
          },
          redirect: 'follow', // manual, *follow, error
          referrerPolicy: 'no-referrer', // no-referrer, *client
          body: {
            "username": username,
            "password": password,
            "grant_type": "password",
            "scope": "",
            "client_id": "",
            "client_secret": ""
          }
        });
    console.log('Completed!', response);
    } catch(err) {
    console.error(`Error: ${err}`);
    }

    window.location.href = '/';
    }
    else
    {
        alert ('Заполните все поля');
    }

});