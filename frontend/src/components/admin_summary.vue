<template>
    <div id = "admin_summary">

        <div v-if = "apiError" class = "error"> {{ apiError }} </div>
        
        <h2> Summary Dashboard </h2>

        <div class = "nav">

            <button @click = "$router.push('/api/admin/dashboard')" class = "return"> <i class = "bi bi-box-arrow-left"> </i> Back to Dashboard </button>

        </div>

        <section v-if = "subjectData.length">
            <h3> Subjects Overview </h3>
            <div v-for = "subject in subjectData" :key = "subject.name" class = "subject-block">
                <h4> {{ subject.name }}: {{ subject.description }}</h4>

                <div v-for="chapter in subject.chapters" :key="chapter.name" class="chapter-block">
                    <h5> {{ chapter.name }}: {{ chapter.description }} </h5>
                    
                    <table class = "summary-table">
                        <thead>
                            <tr>
                                <th> Quiz </th>
                                <th> Description </th>
                                <th> Questions </th>
                                <th> Avg Score </th>
                                <th> Attempts </th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for = "quiz in chapter.quiz_data" :key = "quiz.name">
                                <td> {{ quiz.name }} </td>
                                <td> {{ quiz.description }} </td>
                                <td> {{ quiz.question_count }} </td>
                                <td> {{ quiz.average_score }} </td>
                                <td> {{ quiz.attempts }} </td>
                            </tr>
                        </tbody>
                    </table>

                    <div class = "chart-container">
                    
                    <barchart
                        v-if = "chapter.quiz_data.length"
                        :chart-data = "getQuizChartData(chapter.quiz_data)"
                        :chart-options = "barChartOptions"
                        class = "chart"
                    />

                    </div>

                    <div class = "chart-container">

                    <piechart
                        v-if = "chapter.quiz_data.length"
                        :chart-data = "getQuizAttemptsPieData(chapter.quiz_data)"
                        :chart-options = "pieChartOptions"
                        class = "chart"
                    />

                    </div>

                </div>
            </div>
        </section>

        <section v-if = "userData.length" class = "users">
            <h2> User Performance </h2>
            <div v-for = "user in userData" :key = "user.user[0].username" class = "user-block">
                <p>
                    <strong> {{ user.user[0].username }} </strong>
                    <span> ({{ user.user[0].email }}) </span>
                </p>
                <table class = "summary-table" v-if = "user.subjects.length">
                    <thead>
                        <tr>
                            <th> Subject </th>
                            <th> Avg Score </th>
                            <th> Attempts </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for = "sub in user.subjects" :key = "sub.name">
                            <td> {{ sub.name }} </td>
                            <td> {{ sub.average_score }} </td>
                            <td> {{ sub.attempts }} </td>
                        </tr>
                    </tbody>
                </table>

                <div class = "chart-container">
                
                <barchart
                    v-if = "user.subjects.length"
                    :chart-data = "getUserSubjectChartData(user.subjects)"
                    :chart-options = "barChartOptions"
                    class = "chart"
                />

                </div>

                <div class = "chart-container">

                <piechart
                    v-if = "user.subjects.length"
                    :chart-data = "getUserAttemptsPieData(user.subjects)"
                    :chart-options = "pieChartOptions"
                    class = "chart"
                />

                </div>

            </div>
        </section>
    </div>
</template>

<script setup>
    import { ref, onMounted } from 'vue'
    import barchart from '@/components/barchart.vue'
    import piechart from '@/components/piechart.vue'

    import { useRouter } from 'vue-router'

    const router = useRouter();

    const subjectData = ref([]);
    const userData = ref([]);

    const apiError = ref('');

    const barChartOptions = {
        responsive: true,
        plugins: {
            legend: { display: true, position: 'top' },
            title: { display: false }
        },
        scales: {
            y: { beginAtZero: true }
        }
    };

    const piechartOptions = {
        responsive: true,
        plugins: {
            legend: {
                display: true,
                position: 'right'
            }
        }
    }

    onMounted(() => {
    
        fetch("http://localhost:5000/api/admin/summary", {
            headers: {
                'Content-Type': 'application/json',
                'Authentication-Token': localStorage.getItem('auth_token') || ''
            },
            method: "GET"
        })
        .then(async response => {
            if (response.ok) {
                const data = await response.json();
                subjectData.value = data.subject_data;
                userData.value = data.user_data;
            } else {
                apiError.value = 'Failed to load summary data';
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
                    label: 'Average Score',
                    backgroundColor: '#42a5f5',
                    data: quizData.map(q => q.average_score)
        }]}}

    function getQuizAttemptsPieData(quizData) {
        return {
            labels: quizData.map(q => q.name),
            datasets: [
                {
                    label: 'Attempts',
                    backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF'],
                    data: quizData.map(q => q.attempts)
                }
            ]
        }
    }

    function getUserSubjectChartData(subjects) {
        return {
            labels: subjects.map(s => s.name),
            datasets: [
            {
                label: 'Average Score',
                backgroundColor: '#ffb300',
                data: subjects.map(s => s.average_score)
        }]}}

    function getUserAttemptsPieData(subjects) {
        return {
            labels: subjects.map(s => s.name),
            datasets: [
                {
                    label: 'Attempts',
                    backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF'],
                    data: subjects.map(s => s.attempts)
                }
            ]
        }
    }

</script>

<style scoped>

    #admin_summary {
        max-width: 900px;
        margin: 30px auto;
        padding: 24px 32px;
        background: #f7faff;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        font-family: 'Segoe UI', 'Arial', sans-serif;
    }

    .subject-block, .user-block {
        margin-bottom: 2rem;
        padding: 1rem;
        border-radius: 30px;
    }

    .subject-block {
        background-color: #c1bebe;
    }

    h2 {
        font-size: 2.1em;
        font-weight: 700;
        color: black;
    }

    h4 {
        font-size: 1.8em;
        font-weight: 600;
        color: black;
    }

    h5 {
        font-size: 1.5em;
        font-weight: 500;
        color: black;
    }

    .chapter-block {
        margin-bottom: 1.5rem;
        padding-left: 1rem;
        border-left: 3px solid #2196f3;
        border-radius: 30px;
    }

    .chapter-block:nth-child(even), .user-block:nth-child(even) {
        background: #beafa0;

    }

    .chapter-block:nth-child(odd), .user-block:nth-child(odd) {
        background: #b19f9f;

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

    .users {
        margin-top: 3rem;
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
        margin-top: none;
        margin-bottom: none;
        padding-top: none;
        padding-bottom: none;
    }

    .nav .return:hover {
        background-color: #c1bebe;
    }

</style>
