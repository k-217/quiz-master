<template>

<div id = "logout">

    <h3> Logout </h3>
    
    <button @click = "logout" :disabled = "loading"> {{ loading ? "Logging out..." : "Log Me Out!" }} </button>

    <div v-if = "apiError" class = "error"> {{ apiError }} </div>
    <div v-if = "successMessage" class = "success"> {{ successMessage }} </div>
    
</div>

</template>

<script setup>

    import { ref } from 'vue'

    import { useRouter } from 'vue-router'

    const router = useRouter();

    const apiError = ref('');
    const successMessage = ref('');
    const loading = ref(false);

    function logout() {
        apiError.value = "";
        successMessage.value = "";
        loading.value = true;
        fetch(
            "http://localhost:5000/logout",
            {
                headers: {
                    "Content-Type": "application/json",
                    "Authentication-Token": localStorage.getItem("auth_token") || ""
                },
                method: "POST",
            }
        )
        .then(async response => {

            if (response.ok) {
                successMessage.value = "Successfully logged out!";
                localStorage.removeItem("auth_token");
                localStorage.removeItem("user_role");
                setTimeout(() => {router.push('login')}, 2000); 
                apiError.value = "";
            } else {
                apiError.value = "Could not log you out. Please try later.";
            }

        })
        .catch((error) => {
            apiError.value = "Network error: " + error;
        })
        .finally(() => {
            loading.value = false;
        });
    }

</script>

<style scoped>

    #logout {
        max-width: 340px;
        margin: 30px auto;
        padding: 24px 20px 20px 20px;
        background: #fafafa;
        border-radius: 10px;
        box-shadow: 0 2px 16px rgba(0,0,0,0.08);
        text-align: left;
    }

    #logout h3 {
        text-align: center;
        margin-bottom: 18px;
        color: #333;
        font-size: 1.5em;
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

    button:hover {
        background: #696d77;
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

    .success {
        color: #27ae60;
        font-size: 0.92em;
        margin-bottom: 10px;
    }


</style>