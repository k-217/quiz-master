<template>

<div id = "user_dashboard">

    <div v-if = "apiError" class = "error"> {{ apiError }} </div>

    <h3> User Dashboard </h3>

    <div class = "nav"> 
        <button @click = "$router.push('/api/user/summary')" class = "summary"> <i class = "bi bi-bar-chart-line"> </i> Show Summary </button>
        <button @click = "csvReport" class = "report"> <i class = "bi bi-download"> </i> Download CSV Report </button>
        <button @click = "$router.push('/logout')" class = "logout"> <i class = "bi bi-box-arrow-right"> </i> Log Me Out </button>
    </div>

    <div class = "form">
        <input type = "text" v-model = "keyword" placeholder = "Enter keyword: "/>
        <button @click = "search" :disabled = "loading" class = "search"> {{ loading ? "Searching..." : "Search" }} </button>
    </div>

    <div class = "subjects">

        <dialog v-if = "showViewQuizDialog" open>
            <h4> {{ quizData.name }} </h4>
            <p> Description: {{ quizData.description }} </p>
            <p> Duration: {{ quizData.time_duration }} minutes </p>
            <p> Start After: {{ quizData.date_of_quiz }} </p>
            <p>
                <button @click = "closeViewQuizDialog"> Cancel </button>
                <button @click = "$router.push('/api/user/quiz/' + quizData.id)" :disabled = "quizData.attempted || !canStartQuiz(quizData)"> Start </button>
                <button @click = "$router.push('/api/user/quiz/' + quizData.id + '/score')" :disabled = "!quizData.attempted"> My Responses </button>
            </p>
        </dialog>

        <div v-if = "subjectData.length">
            <div v-for = "subject in subjectData" :key = "subject.id" class = "subject">
                <h5> {{ subject.name }}: {{ subject.description }} </h5>
                <div v-for = "chapter in subject.chapters" :key = "chapter.id" class = "chapter">
                    <strong> {{ chapter.name }}: {{ chapter.description }} </strong>
                    <ul>
                        <li v-for = "quiz in chapter.quizzes" :key = "quiz.id">
                            {{ quiz.name }}
                            <button @click = "viewQuiz(quiz)" class = "view"> <i class = "bi bi-info-circle"> </i> </button>
                            <button @click = "$router.push('/api/user/quiz/' + quiz.id)" class =  "start" :disabled = "quiz.attempted || !canStartQuiz(quiz)"> <i class = "bi bi-play-circle"> </i> </button>
                            <button @click = "$router.push('/api/user/quiz/' + quiz.id + '/score')" :disabled = "!quiz.attempted" class = "score"> <i class = "bi bi-eye"> </i> </button>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    
</div>

</template>

<script setup>

    import { ref, onMounted, computed } from 'vue'

    import { useRouter } from 'vue-router'

    const router = useRouter();

    const keyword = ref('');

    const apiError = ref('');
    const loading = ref(false);

    const subjectData = ref([]);

    const showViewQuizDialog = ref(false);

    const quizData = ref({});

    onMounted( () => {

        loading.value = true;
        fetch(
            "http://localhost:5000/api/user/dashboard",
            {
                headers: {
                    "Content-Type": "application/json",
                    "Authentication-Token": localStorage.getItem("auth_token") || ""
                },
                method: "GET"
            }
        )
        .then(async response => {
            if (response.ok) {
                const data = await response.json();
                subjectData.value = data.subject_data;
                apiError.value = "";
            } else if (response.status === 401) {
                apiError.value = "Unauthorized Access: login first.";
            } else if (response.status === 403) {
                apiError.value = "Forbidden: you do not have permission to access this resource.";
            } else {
                apiError.value = "Failed to load data.";
            }
        })
        .catch((error) => {
            apiError.value = "Network Error: " + error;
        })
        .finally(() => {
            loading.value = false;
        })

    })

    function search() {
        apiError.value = "";
        loading.value = true;
        fetch(
            "http://localhost:5000/api/user/dashboard",
            {
                headers: {
                    "Content-Type": "application/json",
                    "Authentication-Token": localStorage.getItem("auth_token") || ""
                },
                method: "POST",
                body: JSON.stringify({"query": keyword.value})
            }
        )
        .then(async response => {

            if (response.ok) {
                const data = await response.json();
                subjectData.value = data.subject_data;
                apiError.value = "";
                keyword.value = "";
            } else if (response.status === 401) {
                apiError.value = "Unauthorized Access: login first.";
            } else if (response.status === 403) {
                apiError.value = "Forbidden: you do not have permission to access this resource.";
            } else {
                apiError.value = "Could not search. Please try later.";
            }

        })
        .catch((error) => {
            apiError.value = "Network error: " + error;
        })
        .finally(() => {
            loading.value = false;
        });
    }

    function parseBackendDate(str) {
        // str: "YYYY-MM-DD HH:MM:SS"
        // converts to "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        const iso = str.replace(' ', 'T');
        return new Date(iso);
    }

    function canStartQuiz(quiz) {
    const now = new Date();
    const quizStart = parseBackendDate(quiz.date_of_quiz);
    return now >= quizStart;
    }


    function viewQuiz(quiz) {
        showViewQuizDialog.value = true;
        quizData.value = quiz;
    }

    function closeViewQuizDialog() {
        showViewQuizDialog.value = false;
        quizData.value = {};
    }

    function csvReport() {
        fetch(
            "http://localhost:5000/api/user/export",
            {
                headers: {
                    "Content-Type": "application/json",
                    "Authentication-Token": localStorage.getItem("auth_token") || ""
                },
                method: "GET",
            }
        )
        .then(async response => {
            console.log(response);
        })
        .catch((error) => {
            apiError.value = "Network Error: " + error;
        });
    }

</script>

<style scoped>

    #user_dashboard {
        max-width: 900px;
        margin: 30px auto;
        padding: 24px 32px;
        background: #f7faff;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        font-family: 'Segoe UI', 'Arial', sans-serif;
    }

    h3 {
        margin-bottom: 18px;
        color: #333;
        font-size: 1.5em;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    .subjects {
        margin-top: 20px;
        text-align: left;
    }

    .subject {
        margin-bottom: 24px;
        padding: 10px 15px;
        background: #eaf1fb;
        border-radius: 8px;
        border-left: 4px solid #000000;
        transition: box-shadow 0.2s;
        text-align: left;
    }

    .subject h5 {
        margin: 0 0 8px 0;
        font-size: 1.3em;
        color: #000000;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 5px;
    }

    .chapter:nth-child(odd) {
        margin-bottom: 10px;
        padding-left: 16px;
        text-align: left;
        background-color: #b7c2c7;
        border-radius: 10px;
        color: #000000;
    }

    .chapter:nth-child(even) {
        margin-bottom: 10px;
        padding-left: 16px;
        text-align: left;
        background-color: #707379;
        border-radius: 10px;
        color: #ffffff;
    }

    .chapter:nth-child(odd) strong {
        color: #000000;
        font-size: 1.2em;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 5px;
    }

    .chapter:nth-child(even) strong {
        color: #fff;
        font-size: 1.2em;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 5px;
    }

    .chapter:nth-child(even) .view, .start, .score {
        padding: 3px 3px;
        color: #ffffff;
        border: none;
        border-radius: 5px;
        font-size: 0.95em;
        font-weight: 600;
        cursor: pointer;
        transition: background 0.2s;
        background: none;
    }

    .chapter:nth-child(even) .view:disabled, .start:disabled, .score:disabled {
        color: #dbe1f0;
        cursor: not-allowed;
    }

    .chapter:nth-child(odd) .view, .start, .score {
        padding: 3px 3px;
        color: #000000;
        border: none;
        border-radius: 5px;
        font-size: 0.95em;
        font-weight: 600;
        cursor: pointer;
        transition: background 0.2s;
        background: none;
    }

    .chapter:nth-child(odd) .view:disabled, .start:disabled, .score:disabled {
        color: #242427;
        cursor: not-allowed;
    }

    ul {
        margin: 6px 0 6px 0;
        padding-left: 20px;
        font-size: 1.0em;
    }

    li {
        margin-bottom: 4px;
        font-size: 1em;
    }


    .form {
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .form label {
        display: block;
        margin-bottom: 6px;
        font-weight: 600;
        color: #444;
    }

    .form button {
        width: 20%;
        padding: 8px 12px;
    }

    input {
        width: 100%;
        padding: 7px 10px;
        border: 1px solid #bbb;
        border-radius: 5px;
        font-size: 1em;
        box-sizing: border-box;
        background: #fff;
        transition: border 0.2s;
    }

    input:focus {
        border-color: #000000;
        outline: none;
    }

    .search {
        width: 100%;
        padding: 10px 0;
        border: #000000;
        background-color: #fff;
        border-radius: 5px;
        font-size: 1.1em;
        font-weight: 700;
        cursor: pointer;
        transition: background 0.2s;
        margin-top: 6px;
    }

    .search:disabled {
        background: #a7b6d8;
        cursor: not-allowed;
    }

    .search:hover {
        background: #000000;
        color: #fff;
    }

    .view, .start, .score {
        padding: 3px 3px;
        color: #ffffff;
        border: none;
        border-radius: 5px;
        font-size: 0.95em;
        font-weight: 600;
        cursor: pointer;
        transition: background 0.2s;
        background: none;
    }

    .view:disabled, .start:disabled, .score:disabled {
        padding: 3px 3px;
        color: #dbe1f0;
        border: none;
        border-radius: 5px;
        font-size: 0.95em;
        font-weight: 600;
        cursor: not-allowed;
        transition: background 0.2s;
        background: none;
    }


    .error {
        color: #c0392b;
        font-size: 0.92em;
        margin-bottom: 10px;
    }

    dialog[open] {
        border: none;
        border-radius: 8px;
        padding: 24px 32px;
        background: #fff;
        box-shadow: 0 4px 24px rgba(52,107,235,0.14);
        min-width: 20%;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        gap: 14px;
        z-index: 100;
        font-size: 1em;
    }

    dialog h4 {
        font-size: 1.5em;
    }

    dialog button {
        width: 40%;
        margin-top: 8px;
        padding: 8px;
        border-radius: 5px;
        font-size: 0.95em;
        font-weight: 600;
        border: none;
        cursor: pointer;
        transition: background 0.2s;
        background: #000000;
        color: #fffcfc;
    }

    dialog button:hover {
        background: #fffdfd;
        color: #000000;
    }

    dialog button:disabled {
        background: #696d77;
        color: #ffffff;
        cursor: not-allowed;
    }

    .nav {
        width: 100%;
        padding: 10px 0;
        border: none;
        background-color: #000000;
        border-radius: 10px;
        font-size: 1.1em;
        font-weight: 700;
        cursor: pointer;
        transition: background 0.2s;
        margin-top: 6px;
        margin-bottom: 6px;
        align-content: left;
    }

    .nav .summary, .logout, .report {
        width: fit-content;
        border: none;
        background-color: #fff;
        color: #000000;
        border-radius: 10px;
        font-size: 1.1em;
        font-weight: 700;
        cursor: pointer;
        transition: background 0.2s;
        margin-top: none;
        margin-bottom: none;
        padding-top: none;
        padding-bottom: none;
    }

    .nav .summary:hover, .logout:hover {
        background-color: #c1bebe;
    }

    .nav .summary {
        margin-right: 10%;
    }

    .nav .logout {
        margin-left: 10%;
    }

</style>