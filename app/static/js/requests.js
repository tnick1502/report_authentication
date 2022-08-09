let button = document.getElementById('post-btn');

button.addEventListener('click', async _ => {
    les username = document.getElementById('username').value;
    let password = document.getElementById('password').value;
    try {
    let response = await fetch('/', {
          method: 'post',
          headers: {
            "Content-type": "application/json"
          },
          body: {
            "username": username,
            "password": password,
            "grant_type": "password",
            "scope": "",
            "client_id": "",
            "client_secret": ""
          }
        });
    console.log(username)
    console.log(password)
    console.log('Completed!', response);
    } catch(err) {
    console.error(`Error: ${err}`);
    }
});