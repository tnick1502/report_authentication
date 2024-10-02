export async function signOut(setLogged) {
    await fetch(`${process.env.REACT_APP_SERVER_IP}auth/sign-out/`, {
      method: "GET", // *GET, POST, PUT, DELETE, etc.
      credentials: "include", // include, *same-origin, omit
    }).then((response) => {
      if (!response.ok) {
        setLogged(false);
      } else {
        setLogged(false);
      }
    });
}

 
export async function login(setLogged, username, password) {
    await fetch(`${process.env.REACT_APP_SERVER_IP}auth/sign-in/`, {
      method: "POST", // *GET, POST, PUT, DELETE, etc.
      credentials: "include", // include, *same-origin, omit
      headers: {
        Accept: "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        // 'Content-Type': 'application/x-www-form-urlencoded',
        "X-Requested-With": "XMLHttpRequest",
      },
      body: `grant_type=password&username=${username}&password=${password}`,
    }).then((response) => {
      if (!response.ok || response.status !== 200) {
        setLogged(false);
        const inputs = document.querySelectorAll("#login-form input");
        inputs.forEach((input) => {
          input.classList.remove("is-valid");
          input.classList.add("is-invalid");
        });
      } else {
        setLogged(true);
      }
    });
  }