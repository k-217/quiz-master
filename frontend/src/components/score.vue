<template>

    <div id = "score">
        
        <div v-if = "apiError" class = "error"> {{ apiError }} </div>

        <div v-if = "loading"> <p class = "error"> loading... </p> </div>

        <div v-else>
            <h3> {{ subjectName }} </h3>
            <h4> {{ chapterName }} </h4>
            <h5> {{ quizName }} </h5>

            <div class = "score-summary">
                <span class = "score-label"> Score: </span>
                <span class = "score-value"> {{ score }}% </span>
            </div>

            <div v-for = "(question, idx) in questions" :key = "question.id" class = "questions" :class = "idx % 2 === 0 ? 'odd' : 'even'">
                <div class = "question-text"> {{ question.text }} </div>
                <div class = "options">
                    <div v-for = "i in 4" :key = "i">
                        <input 
                            type = "radio" 
                            :id = "'q_' + question.id + '_' + i" 
                            :checked = "question.option_marked === i" 
                            disabled 
                        />
                        <label 
                            :class = "{ 
                                correct: question.correct_option === i, 
                                marked: question.option_marked === i && !question.option_correct,
                            }"
                        >
                        {{ question['option' + i] }}
                        <span v-if = "question.correct_option === i" class = "correct-badge"> Correct </span>
                        <span v-if = "question.option_marked === i && !question.option_correct" class = "wrong-badge"> Your Answer </span>
                        </label>
                    </div>
                </div>
                <div v-if = "question.option_marked === 0" class = "not-attempted">
                    Not attempted
                </div>
            </div>

            <button @click = "$router.push('/api/user/dashboard')" class = "back"> Back to Dashboard </button>
        
        </div>
    </div>

</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute();

const subjectName = ref('');
const chapterName = ref('');
const quizName = ref('');
const questions = ref([]);
const score = ref(0);

const apiError = ref('');
const loading = ref(true);

const quizId = route.params.quiz_id;

onMounted(() => {
    loading.value = true;
    fetch(
        "http://localhost:5000/api/user/quiz/" + quizId + "/score",
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
            const subj = data.subject_data;
            subjectName.value = subj.subject[0];
            chapterName.value = subj.chapter[0];
            quizName.value = subj.quiz[0];
            score.value = subj.score[0];
            questions.value = subj.responses.map(obj => {
                const key = Object.keys(obj)[0];
                return { id: key, ...obj[key] };
            });
            apiError.value = "";
        } else {
            apiError.value = "Failed to load score.";
        }
    })
    .catch(error => {
        apiError.value = "Network Error: " + error;
    })
    .finally(() => {
        loading.value = false;
    });
});

</script>

<style scoped>

    #score {
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

    .score-summary {
        margin-bottom: 24px;
        font-size: 1.2em;
        background: #eaf1fb;
        padding: 12px 18px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        gap: 10px;
        width: fit-content;
    }

    .score-label {
        color: #333;
        font-weight: 600;
    }

    .score-value {
        color: #1d7d3e;
        font-weight: 700;
        font-size: 1.3em;
    }

    .questions {
        margin-bottom: 10px;
        text-align: left;
        border-radius: 10px;
        padding: 16px;
        background-color: #b7c2c7;
        color: #000000;
    }

    .questions.even {
        background-color: #707379;
        color: #ffffff;
    }

    .question-text {
        font-weight: 500;
        margin-bottom: 8px;
    }

    .options {
        padding-bottom: 10px;
    }

    input {
        margin-right: 6px;
    }

    label {
        margin-right: 10px;
        font-size: 1em;
        padding: 2px 6px;
        border-radius: 4px;
    }

    label.correct {
        background-color: #d4edda;
        color: #155724;
        font-weight: 600;
    }

    label.marked {
        background-color: #f8d7da;
        color: #721c24;
        font-weight: 600;
    }

    .correct-badge, .wrong-badge {
        margin-left: 5px;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.7em;
    }

    .correct-badge {
        background: #1d7d3e;
        color: #fff;
    }

    .wrong-badge {
        background: #c0392b;
        color: #fff;
    }

    .not-attempted {
        color: #ce1500;
        font-size: 0.98em;
        margin-top: 6px;
        font-style: italic;
    }

    .error {
        color: #c0392b;
        font-size: 0.92em;
        margin-bottom: 10px;
    }

    .back {
        width: 100%;
        padding: 10px 0;
        background-color: #000000;
        border-radius: 5px;
        font-size: 1.1em;
        font-weight: 700;
        cursor: pointer;
        transition: background 0.2s;
        margin-top: 16px;
        color: #fff;
    }

    .back:hover {
        background: #ffffff;
        color: #000000;
    }

</style>
