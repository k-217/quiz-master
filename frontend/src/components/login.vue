<template>

<div id = "login">

    <h3> Login </h3>

    <div class = "form">
        <label> Your Email: </label> <input type = "email" v-model = "email"/>
    </div>
    
    <div class = "form">
        <label> Your Username: </label> <input type = "text" v-model = "username"/>
    </div>
    
    <div class = "form">
        <label> Your Password: </label> <input type = "password" v-model = "password"/>
    </div>

    <div v-if = "validate" class = "error"> {{ validate }} </div>
    
    <button @click = "login" :disabled = "!!validate || loading"> Log Me In! </button> <br/> <br/>

    <button @click = "$router.push('/register')" :disabled = "loading"> New User, Register Here! </button>

    <div v-if="apiError" class = "error"> {{ apiError }} </div>
    
</div>

</template>

<script setup>

    import { ref, computed } from 'vue'

    // ref: reactive reference

    import { useRouter } from 'vue-router'

    const router = useRouter();

    const email = ref('');
    const username = ref('');
    const password = ref('');

    const loading = ref(false);

    const validate = computed(() => {

        if (!email.value) return 'Email is required'
        
        if (!username.value) return 'Username is required'
        
        if (!password.value) return 'Password is required'
        
        return ''
    })

    const apiError = ref('');

    function login() {
        loading.value = true;
        apiError.value = "";
        if (!email.value || !username.value || !password.value){
            apiError.value = "Please fill in all required details.";
            return;
        } else {
            const data = {"email": email.value, "username": username.value, "password": password.value}
            fetch(
                "http://localhost:5000/login?include_auth_token", // query_param: include_auth_token
                {
                    headers: {
                        "Content-Type": "application/json",
                    },
                    method: "POST",
                    body: JSON.stringify(data)
                }
            )
            .then(async response => {
                if (response.ok) {
                    const respData = await response.json();
                    console.log(respData);
                    if (respData.response.user.authentication_token) {
                        localStorage.setItem('auth_token', respData.response.user.authentication_token)
                        fetch("http://localhost:5000/api/me", {
                            headers: {
                                "Content-Type": "application/json",
                                "Authentication-Token": localStorage.getItem('auth_token')
                            }
                        })
                        .then(async response => {
                            if (response.ok){
                                const r = await response.json();
                                console.log(r);
                                const roles = r.roles || [];
                                localStorage.setItem('user_role', roles);
                                if (roles.includes('admin')) {
                                    router.push('api/admin/dashboard');
                                } else if (roles.includes('user')) {
                                    router.push('api/user/dashboard');
                                }
                            } else {
                                apiError.value = "Can not login. Please try later."
                            }
                        })
                        .catch((error) => {
                            apiError.value = "Failed to fetch user info: " + error;
                        });
                    }
                } else {
                    apiError.value = "Can not login. Please try later.";
                } 
            })
            .catch((error) => {
                apiError.value = "Network error: " + error;
            })
            .finally(() => {
                loading.value = false;
            });
        }
    }

</script>

<style scoped>

    #login {
        max-width: 340px;
        margin: 30px auto;
        padding: 24px 20px 20px 20px;
        background: #fafafa;
        border-radius: 10px;
        box-shadow: 0 2px 16px rgba(0,0,0,0.08);
        text-align: left;
    }

    #login h3 {
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
        font-size: 0.9em;
        font-weight: 700;
        cursor: pointer;
        transition: background 0.2s;
    }

    button:hover {
        background:#696d77;
    }

    button:disabled {
        background: #696d77;
        cursor: not-allowed;
    }

    .error {
        color: #c0392b;
        font-size: 0.92em;
        margin-bottom: 10px;
    }

</style>