<template>

<div id = "register">

    <h3> Register </h3>

    <div class = "form">
        <label> Enter Email: </label> <input type = "email" v-model = "email"/>
    </div>
    
    <div class = "form">
        <label> Enter Username: </label> <input type = "text" v-model = "username"/>
    </div>
    
    <div class = "form">
        <label> Enter Password: </label> <input type = "password" v-model = "password"/>
    </div>

    <div v-if = "validate" class = "error"> {{ validate }} </div>
    
    <button @click = "register" :disabled = "!!validate || loading"> {{ loading ? "Registering..." : "Register Me!" }} </button>

    <button @click = "$router.push('/login')" :disabled="loading"> Existing User, Login Here! </button>

    <div v-if = "apiError" class = "error"> {{ apiError }} </div>
    <div v-if = "successMessage" class = "success"> {{ successMessage }} </div>
    
</div>

</template>

<script setup>

    import { ref, computed } from 'vue'

    import { useRouter } from 'vue-router'

    const router = useRouter();

    const email = ref('');
    const username = ref('');
    const password = ref('');

    const usernamePattern = /^[a-zA-Z0-9]{4,}$/
    const passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W)(?!.*\s).{8,}$/
    const emailPattern = /^[^@\s]+@[^@\s]+\.[^@\s]+$/

    const validate = computed(() => {

        if (!email.value) return 'Email is required'
        if (!emailPattern.test(email.value)) return 'Email must be in the format: name@domain.tld'
        
        if (!username.value) return 'Username is required'
        if (!usernamePattern.test(username.value)) return 'Username: Min 4 chars, no spaces'
        
        if (!password.value) return 'Password is required'
        if (!passwordPattern.test(password.value)) return 'Password: Min 8 chars, at least one uppercase, at least one lowercase, at least one numerical, at least one special char, no spaces'
        
        return ''
    })

    const apiError = ref('');
    const successMessage = ref('');
    const loading = ref(false);

    function register() {
        apiError.value = "";
        successMessage.value = "";
        loading.value = true;
        const data = {"email": email.value, "username": username.value, "password": password.value}
        fetch(
            "http://localhost:5000/register?include_auth_token",
            {
                headers: {
                    "Content-Type": "application/json",
                },
                method: "POST",
                body: JSON.stringify(data)
            }
        )
        .then(async response => {

            const respData = await response.json();

            if (response.ok) {
                // any status code from 200-299
                const token = respData.response.user.authentication_token;
                if (token) {
                    localStorage.setItem("auth_token", token);
                    localStorage.setItem("user_role", ['user']);
                    successMessage.value = "Successfully registered! Redirecting to dashboard...";
                    setTimeout(() => {router.push('api/user/dashboard')}, 2000);   
                    email.value = "";
                    username.value = "";
                    password.value = "";
                    apiError.value = "";
                } else {
                    apiError.value = "Authentication Token not found!";
                }
            } else {
                apiError.value = "Error: "+ (String(respData.response?.errors) || "Registration failed. Please try later.");
            }

        })
        .catch((error) => {
            apiError.value = "Network error: " + error;
        })
        .finally(() => {
            loading.value = false
        });
    }

</script>

<style scoped>

    #register {
        max-width: 340px;
        margin: 30px auto;
        padding: 24px 20px 20px 20px;
        background: #fafafa;
        border-radius: 10px;
        box-shadow: 0 2px 16px rgba(0,0,0,0.08);
        text-align: left;
    }

    #register h3 {
        text-align: center;
        margin-bottom: 18px;
        color: #333;
        font-size: 1.5em;
    }

    .form {
        margin-bottom: 15px;
    }

    .form label {
        display: block;
        margin-bottom: 6px;
        font-weight: 600;
        color: #444;
    }

    input {
        width: 100%;
        padding: 7px 10px;
        border: 1px solid #bbb;
        border-radius: 5px;
        font-size: 1em;
        box-sizing: border-box;
    }

    button {
        width: 100%;
        padding: 10px 0;
        background: #000000;
        color: #fff;
        border: none;
        border-radius: 5px;
        font-size: 1.1em;
        font-weight: 700;
        cursor: pointer;
        transition: background 0.2s;
    }

    button:disabled {
        background: #696d77;
        cursor: not-allowed;
    }

    button:hover {
        background: #696d77;
    }

    .error {
        color: #c0392b;
        font-size: 0.92em;
        margin-bottom: 10px;
    }

    .success {
        color: #27ae60;
        font-size: 0.92em;
        margin-bottom: 10px;
    }


</style>