<template>
    <div id = "user_summary">
    
        <div v-if = "apiError" class = "error"> {{ apiError }} </div>

        <h2> My Summary </h2>

        <div class = "nav">
          <button @click = "$router.push('/api/user/dashboard')" class = "return"> <i class = "bi bi-box-arrow-left"> </i> Back to Dashboard </button>
        </div>

        <section v-if="summaryData.length">
            
            <h3> Subjects Overview </h3>
            
            <div v-for="subject in summaryData" :key="subject.name" class="subject-block">
                <h4> {{ subject.name }}: {{ subject.description }} </h4>

                <div v-for="chapter in subject.chapters" :key="chapter.name" class="chapter-block">
                    <h5> {{ chapter.name }}: {{ chapter.description }} </h5>

                    <table class = "summary-table" v-if = "chapter.quizzes.length">
                        <thead>
                            <tr>
                                <th> Quiz </th>
                                <th> Score </th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for = "quiz in chapter.quizzes" :key = "quiz.name">
                                <td> {{ quiz.name }} </td>
                                <td> {{ quiz.score }} </td>
                            </tr>
                        </tbody>
                    </table>

                    <div class = "chart-container">
                        <barchart
                            v-if = "chapter.quizzes.length"
                            :chart-data = "getQuizChartData(chapter.quizzes)"
                            :chart-options = "barChartOptions"
                            class = "chart"
                        />
                    </div>
                </div>
            </div>
        </section>
    </div>
</template>

<script setup>
    import { ref, onMounted } from 'vue'
    import barchart from '@/components/barchart.vue'
    import { useRouter } from 'vue-router'

    const router = useRouter();
    const summaryData = ref([]);
    const apiError = ref('');

    const barChartOptions = {
        responsive: true,
        plugins: {
            legend: { display: false },
            title: { display: false }
        },
        scales: {
            y: { beginAtZero: true }
        }
    };

    onMounted(() => {
        fetch("http://localhost:5000/api/user/summary", {
        headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': localStorage.getItem('auth_token') || ''
        },
        method: "GET"
        })
        .then(async response => {
            if (response.ok) {
                const data = await response.json();
                summaryData.value = data.summary_data;
            } else {
                apiError.value = "Failed to load summary data.";
            }
        })
        .catch((error) => {
            apiError.value = "Network Error: " + error;
        });
    })

    function getQuizChartData(quizData) {
        return {
            labels: quizData.map(q => q.name),
            datasets: [
                {
                    label: 'Score',
                    backgroundColor: '#42a5f5',
                    data: quizData.map(q => q.score)
        }]}}


</script>

<style scoped>
    #user_summary {
        max-width: 900px;
        margin: 30px auto;
        padding: 24px 32px;
        background: #f7faff;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        font-family: 'Segoe UI', 'Arial', sans-serif;
    }

    h2 {
        font-size: 2.1em;
        font-weight: 700;
        color: black;
    }

    h4 {
        font-size: 1.5em;
        font-weight: 600;
        color: black;
    }

    h5 {
        font-size: 1.2em;
        font-weight: 500;
        color: black;
    }

    .subject-block {
        margin-bottom: 2rem;
        padding: 1rem;
        border-radius: 20px;
        background-color: #eaf1fb;
    }

    .chapter-block {
        margin-bottom: 1.5rem;
        padding-left: 1rem;
        border-left: 3px solid #2196f3;
        border-radius: 20px;
        background: #b7c2c7;
    }

    .chapter-block:nth-child(even) {
        background: #707379;
        color: #fff;
    }

    .summary-table {
        width: 90%;
        border-collapse: collapse;
        margin-bottom: 1rem;
    }

    .summary-table th, .summary-table td {
        border: 1px solid #e0e0e0;
        padding: 8px;
        text-align: left;
    }

    .summary-table th {
        background: #9f9e9e;
    }

    .chart-container {
        width: 50%;
        height: 200px;
    }

    .chart {
        max-width: 600px;
        margin: 1rem 0;
    }

    .error {
        color: #c0392b;
        font-size: 0.92em;
        margin-bottom: 10px;
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

    .nav .return {
        width: fit-content;
        border: none;
        background-color: #fff;
        color: #000000;
        border-radius: 10px;
        font-size: 1.1em;
        font-weight: 700;
        cursor: pointer;
        transition: background 0.2s;
    }

    .nav .return:hover {
        background-color: #c1bebe;
    }

</style>
