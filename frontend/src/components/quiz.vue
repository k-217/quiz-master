<template>

    <div id = "quiz">

        <div v-if = "apiError" class = "error"> {{ apiError }} </div>

        <div v-if = "loading">
            <p class = "error"> loading... </p>
        </div>

        <div v-else>

            <dialog v-if = "showAfterQuizDialog" open>
                Congratulations on completing {{ afterQuiz.quiz }} ({{ afterQuiz.subject }}: {{ afterQuiz.chapter }})! 
                You have scored {{ afterQuiz.score }}%! 
                <button @click = "$router.push('/api/user/dashboard')"> Back to Dashboard </button>
            </dialog>

            <h3> {{ subjectName }} </h3>

            <h4> {{ chapterName }} </h4>

            <h5> {{ quizName }} </h5>

            <div class = "timer1">

                <div v-if = "!showAfterQuizDialog" class = "timer">
                    {{ Math.floor(timeLeft / 60).toString().padStart(2, '0') }}:{{ (timeLeft % 60).toString().padStart(2, '0') }}
                </div>
            
            </div>

            <div v-for = "question in questions" class = "questions">
                {{ question.text }}
                <div class = "options">
                    <br/>
                    <input type = "radio" :id = "'q_' + question.id + '_1'" :value = "1" :name = "'question_' + question.id"/> <label> {{ question.option1 }} </label> <br/>
                    <input type = "radio" :id = "'q_' + question.id + '_2'" :value = "2" :name = "'question_' + question.id"/> <label> {{ question.option2 }} </label> <br/>
                    <input type = "radio" :id = "'q_' + question.id + '_3'" :value = "3" :name = "'question_' + question.id"/> <label> {{ question.option3 }} </label> <br/>
                    <input type = "radio" :id = "'q_' + question.id + '_4'" :value = "4" :name = "'question_' + question.id"/> <label> {{ question.option4 }} </label> <br/>
                </div>
                <button @click = "clear(question.id)" class = "clear"> Clear </button>
            </div>

            <button @click = "submitQuiz" class = "submit"> Submit </button>

        </div>

    </div>

</template>

<script setup>

    import { ref, onMounted, onUnmounted } from 'vue';
    
    import { useRoute } from 'vue-router';
    
    const route = useRoute();

    const subjectName = ref('');
    const chapterName = ref('');
    const quizName = ref('');
    const quizDuration = ref(0);
    const questions = ref([]);

    const apiError = ref('');

    const loading = ref(true);

    const quizId = route.params.quiz_id;

    const afterQuiz = ref({});
    const showAfterQuizDialog = ref(false);

    const timeLeft = ref(quizDuration);
    let timerInterval = null;

    onMounted( () => {

        loading.value = true;

        fetch(
            "http://localhost:5000/api/user/quiz/" + quizId + "/start",
            {
                headers: {
                    "Content-Type": "application/json",
                    "Authentication-Token": localStorage.getItem("auth_token") || ""
                },
                method: "GET"
            }
        )
        .then(
            async response => {
                if (response.ok) {
                    const data = await response.json();
                    subjectName.value = data.subject_data.name;
                    chapterName.value = data.subject_data.chapter.name;
                    quizName.value = data.subject_data.chapter.quiz.name;
                    quizDuration.value = data.subject_data.chapter.quiz.time_duration;
                    questions.value = data.subject_data.chapter.quiz.questions;

                    timerInterval = setInterval(() => {
                        if (timeLeft.value > 0) {
                            timeLeft.value--;
                        } else {
                            clearInterval(timerInterval);
                            submitQuiz(); // auto-submit when time is up
                        }
                    }, 1000);

                } else {
                    apiError.value = "Failed to load quiz. Please try again later.";
                }
            }
        )
        .catch( (error) => {
            apiError.value = error;
        })

        loading.value = false;

    });

    function clear(questionId) {
        const radios = document.getElementsByName('question_' + questionId);
        radios.forEach(radio => {
            radio.checked = false;
        });
    }

    function submitQuiz(){
        
        const responses = {};
        questions.value.forEach(question => {
            let chosen = null;
            for (let i = 1; i <= 4; i++) {
                const radio = document.getElementById(`q_${question.id}_${i}`);
                if (radio && radio.checked) {
                    chosen = i;
                    break;
                }
            }
            responses[question.id] = chosen;

            if (!responses.hasOwnProperty(question.id)) {
                responses[question.id] = null;
            }
        });
        
        fetch(
            "http://localhost:5000/api/user/quiz/" + quizId + "/end",
            {
                headers: {
                    "Content-Type": "application/json",
                    "Authentication-Token": localStorage.getItem("auth_token") || ""
                },
                method: "POST",
                body: JSON.stringify(responses)
            }
        )
        .then(async response => {
            
            if (response.ok) {
                const data = await response.json();
                afterQuiz.value = data;
            } else {
                apiError.value = "Failed to submit quiz."
            }

        })
        .catch( (error) => {
            apiError.value = "Network Error: "+ error
        })
        .finally( () => {
            showAfterQuizDialog.value = true;
        })
    }

    onUnmounted(() => {
        if (timerInterval) clearInterval(timerInterval);
    });

</script>

<style scoped>

    #quiz {
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
        font-size: 1.8em;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    h4 {
        margin-bottom: 18px;
        color: #333;
        font-size: 1.5em;
        font-weight: 500;
        letter-spacing: 0.5px;
    }

    h5 {
        margin-bottom: 18px;
        color: #333;
        font-size: 1.2em;
        font-weight: 400;
        letter-spacing: 0.5px;
    }

    .questions:nth-child(odd) {
        margin-bottom: 10px;;
        text-align: left;
        background-color: #b7c2c7;
        border-radius: 10px;
        color: #000000;
        padding: 16px;
    }

    .questions:nth-child(even) {
        margin-bottom: 10px;
        text-align: left;
        background-color: #707379;
        border-radius: 10px;
        color: #ffffff;
        padding: 16px;
    }

    .questions:nth-child(odd) strong {
        color: #000000;
        font-size: 1.2em;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 5px;
    }

    .questions:nth-child(even) strong {
        color: #fff;
        font-size: 1.2em;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 5px;
    }

    .questions:nth-child(even) .clear {
        background-color: #707379;
        color: #fff;
        font-size: 0.7em;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 5px;
    }

    .questions:nth-child(odd) .clear {
        background-color: #b7c2c7;
        color: #000000;
        font-size: 0.7em;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 5px;
    }

    .questions .options {
        padding-bottom: 10px;
    }

    .submit {
        width: 100%;
        padding: 10px 0;
        background-color: #000000;
        border-radius: 5pxrgb(212, 204, 204);
        font-size: 1.1em;
        font-weight: 700;
        cursor: pointer;
        transition: background 0.2s;
        margin-top: 6px;
        color: #fff;
    }

    .submit:disabled {
        background: #a7b6d8;
        cursor: not-allowed;
    }

    .submit:hover {
        background: #ffffff;
        color: #000000;
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
        color: #000000
    }

    .timer {
        background: black;
        color: white;
        font-size: 1.5em;
        width: 10%;
        border-radius: 5px;
        margin-left: auto;
        margin-right: none;
        margin-top: 10px;
        margin-bottom: 10px;
        vertical-align: middle;
    }


</style>