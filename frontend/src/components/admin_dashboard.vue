<template>

<div id = "admin_dashboard">

    <div v-if = "apiError" class = "error"> {{ apiError }} </div>

    <h3> Admin Dashboard </h3>

    <div class = "nav"> 
        <button @click = "$router.push('/api/admin/summary')" class = "summary"> <i class = "bi bi-bar-chart-line"> </i> Show Summary </button>
        <button @click = "$router.push('/logout')" class = "logout"> <i class = "bi bi-box-arrow-right"> </i> Log Me Out </button>
    </div>

    <div class = "form">
        <input type = "text" v-model = "keyword" placeholder = "Enter keyword: "/>
        <button @click = "search" :disabled = "loading" class = "search"> {{ loading ? "Searching..." : "Search" }} </button>
    </div>
    
    <div class = "subjects">

        <button @click = "openCreateSubjectDialog" class = "create"> <i class = "bi bi-plus"> </i> Subject </button>

        <dialog v-if = "showCreateSubjectDialog" open>
            <label> Name: <input v-model = "newSubject.name" /></label>
            <label> Description: <input v-model = "newSubject.description" /></label>
            <p>
                <button @click = "createSubject"> Create </button>
                <button @click = "closeCreateSubjectDialog"> Cancel </button>
            </p>
        </dialog>

        <dialog v-if = "showCreateChapterDialog" open>
            <label> Name: <input v-model="newChapter.name" /> </label>
            <label> Description: <input v-model="newChapter.description" /> </label>
            <p>
                <button @click = "createChapter"> Create </button>
                <button @click = "closeCreateChapterDialog"> Cancel </button>
            </p>
        </dialog>

        <dialog v-if = "showCreateQuizDialog" open>
            <label> Name: <input v-model = "newQuiz.name" /> </label>
            <label> Description: <input v-model = "newQuiz.description" /> </label>
            <label> Date: <input type="date" v-model = "newQuiz.date" /> </label>
            <label> Duration (minutes): <input type = "number" v-model = "newQuiz.duration" /> </label>
            <p>
                <button @click = "createQuiz"> Create </button>
                <button @click = "closeCreateQuizDialog"> Cancel </button>
            </p>
        </dialog>

        <dialog v-if = "showCreateQuestionDialog" open>
            <label> Question: <input v-model = "newQuestion.text" /> </label>
            <label> Option 1: <input v-model = "newQuestion.option1" /> </label>
            <label> Option 2: <input v-model = "newQuestion.option2" /> </label>
            <label> Option 3: <input v-model = "newQuestion.option3" /> </label>
            <label> Option 4: <input v-model = "newQuestion.option4" /> </label>
            <label> Correct Option (1-4): <input v-model = "newQuestion.correct_option" /> </label>
            <p>
                <button @click = "createQuestion"> Create </button>
                <button @click = "closeCreateQuestionDialog"> Cancel </button>
            </p>
        </dialog>

        <dialog v-if = "showCreateUserDialog" open>
            <label> Username: <input v-model = "newUser.username" /> </label>
            <label> Email: <input v-model = "newUser.email" /> </label>
            <label> Password: <input type = "password" v-model = "newUser.password" /> </label>
            <p>
                <button @click = "createUser"> Create </button>
                <button @click = "closeCreateUserDialog"> Cancel </button>
            </p>
        </dialog>

        <dialog v-if = "showDeleteConfirm" open>
            <p> Are you sure you want to delete {{ itemToDelete }}? </p>
            <p>
                <button @click = "confirmDelete"> Yes, delete! </button>
                <button @click = "cancelDelete"> No, keep! </button>
            </p>
        </dialog>

        <div v-if = "subjectData.length">
            <div v-for = "subject in subjectData" :key = "subject.id" class = "subject">
                
                <template v-if = "!subject.editing">
                    <h5>
                        {{ subject.name }}: {{ subject.description }}
                        <button @click = "startEditSubject(subject)" class = "edit"> <i class = "bi bi-pencil-square"> </i> </button>
                        <button @click = "deleteSubject(subject)" class = "delete"> <i class = "bi bi-trash3"> </i> </button>
                    </h5>
                    <button @click = "openCreateChapterDialog(subject.id)" class = "create"> <i class = "bi bi-plus"> </i> Chapter </button>
                </template>
                
                <template v-else>
                    <h5>
                        <input v-model = "subject.editName" />
                        <input v-model = "subject.editDescription" />
                        <button @click = "saveEditSubject(subject)" class = "save"> Save </button>
                        <button @click = "cancelEditSubject(subject)" class = "cancel"> Cancel </button>
                    </h5>
                </template>

                <div v-for = "chapter in subject.chapters" :key = "chapter.id" class = "chapter">
                    <template v-if="!chapter.editing">
                        <strong> 
                            {{ chapter.name }}: {{ chapter.description }}
                            <button @click = "startEditChapter(chapter)" class = "edit"> <i class = "bi bi-pencil-square"> </i> </button>
                            <button @click = "deleteChapter(chapter)" class = "delete"> <i class = "bi bi-trash3"> </i> </button>
                        </strong>
                        <button @click = "openCreateQuizDialog(chapter.id)" class = "create"> <i class = "bi bi-plus"> </i> Quiz </button>
                    </template>
                    <template v-else>
                        <input v-model = "chapter.editName" />
                        <input v-model = "chapter.editDescription" />
                        <button @click = "saveEditChapter(chapter)" class = "save"> Save </button>
                        <button @click = "cancelEditChapter(chapter)" class = "cancel"> Cancel </button>
                    </template>
                    <ul>
                        <li v-for = "quiz in chapter.quizzes" :key = "quiz.id">
                            <template v-if = "!quiz.editing">
                                <p> 
                                    {{ quiz.name }}: {{ quiz.description }}
                                    <button @click = "startEditQuiz(quiz)" class = "edit"> <i class = "bi bi-pencil-square"> </i> </button>
                                    <button @click = "deleteQuiz(quiz)" class = "delete"> <i class = "bi bi-trash3"> </i> </button>
                                </p>
                            </template>
                            <template v-else>
                                <input v-model = "quiz.editName" />
                                <input v-model = "quiz.editDescription" />
                                <input type = "date" v-model = "quiz.editDate" />
                                <input type = "number" v-model = "quiz.editDuration" />
                                <p> 
                                    <button @click = "saveEditQuiz(quiz)" class = "save"> Save </button>
                                    <button @click = "cancelEditQuiz(quiz)" class = "cancel"> Cancel </button>
                                </p>
                            </template>
                            <ul>
                                <li v-for = "q in quiz.questions" :key = "q.id"> 
                                    <template v-if = "!q.editing">
                                        <p> 
                                            Q: {{ q.text }} 
                                            <button @click = "startEditQuestion(q)" class = "edit"> <i class = "bi bi-pencil-square"> </i> </button>
                                            <button @click = "deleteQuestion(q)" class = "delete"> <i class = "bi bi-trash3"> </i> </button>
                                        </p>
                                        <p> {{ "1. " + q.option1 + " 2. " + q.option2 + " 3. " + q.option3 + " 4. " + q.option4 }} </p>
                                        <p> Correct Option: {{ q.correct_option }} </p>
                                        
                                    </template>
                                    <template v-else>
                                        <input v-model = "q.editText" />
                                        <input v-model = "q.editOption1" />
                                        <input v-model = "q.editOption2" />
                                        <input v-model = "q.editOption3" />
                                        <input v-model = "q.editOption4" />
                                        <input v-model = "q.editCorrectOption" />
                                        <button @click = "saveEditQuestion(q)" class = "save"> Save </button>
                                        <button @click = "cancelEditQuestion(q)" class = "cancel"> Cancel </button>
                                    </template>
                                </li>
                            </ul>
                            <button @click = "openCreateQuestionDialog(quiz.id)" class = "create"> <i class = "bi bi-plus"> </i> Question </button>
                        </li>
                    </ul>
                </div>
            </div>
        </div>

    </div>

    <div v-if = "userData.length" class = "users">
        <h4> Users </h4>
        <button @click = "openCreateUserDialog" class = "create"> <i class = "bi bi-plus"> </i> User </button>
        <ul>
            <li v-for = "user in userData" :key = "user.id"> 
                {{ user.username }}: {{ user.email }} 
                <button @click = "deleteUser(user)" class = "delete"> <i class = "bi bi-trash3"> </i> </button>
            </li>
        </ul>
    </div>
    
</div>

</template>

<script setup>

    import { ref, onMounted } from 'vue'

    import { useRouter } from 'vue-router'

    const router = useRouter();

    const keyword = ref('');

    const apiError = ref('');
    
    const loading = ref(false); // search function loading state

    const subjectData = ref([]);
    const userData = ref([]);

    const showCreateSubjectDialog = ref(false);
    const newSubject = ref({
        name: '',
        description: ''
    });

    const showCreateChapterDialog = ref(false);
    const newChapter = ref({ subject_id: '', name: '', description: '' });

    const showCreateQuizDialog = ref(false);
    const newQuiz = ref({ 
        name: '', 
        description: '', 
        chapter_id: '', 
        date: '', 
        duration: '' 
    });

    const showCreateQuestionDialog = ref(false);
    const newQuestion = ref({ 
        text: '', 
        option1: '', 
        option2: '', 
        option3: '', 
        option4: '', 
        correct_option: '' 
    });

    const showDeleteConfirm = ref(false);
    const itemToDelete = ref(null);
    const deleteAction = ref(null);

    const showCreateUserDialog = ref(false);
    const newUser = ref({
        username: '',
        email: '',
        password: ''
    });

    onMounted( () => {

        loading.value = false;
        fetch(
            "http://localhost:5000/api/admin/dashboard",
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
                userData.value = data.user_data;
                apiError.value = "";
            } else if (response.status === 401) {
                apiError.value = "Unauthorized Access 401: login first.";
            } else if (response.status === 403) {
                apiError.value = "Forbidden 403: you do not have permission to access this resource.";
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
            "http://localhost:5000/api/admin/dashboard",
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
                userData.value = data.user_data;
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

    // create subject

    function openCreateSubjectDialog() { 
        showCreateSubjectDialog.value = true; 
    }
    
    function createSubject() {
        if (!newSubject.value.name || !newSubject.value.description) {
            apiError.value = "Please fill in all fields.";
            return;
        }
        const data = {
            name: newSubject.value.name,
            description: newSubject.value.description
        }
        fetch(
            "http://localhost:5000/api/admin/subject/create",
            {
                headers: {
                    "Content-Type": "application/json",
                    "Authentication-Token": localStorage.getItem("auth_token") || ""
                },
                method: "POST",
                body: JSON.stringify(data)
            }
        )
        .then(async response => {
            if (response.ok) {
                apiError.value = "Subject created successfully. Reload to view updated dashboard.";
            } else {
                apiError.value = "Failed to create subject.";
            }
        })
        .catch((error) =>{
            apiError.value = "Network error: " + error;
        })
        .finally(() => {
            showCreateSubjectDialog.value = false;
            newSubject.value.name = '';
            newSubject.value.description = '';
        })
        
    }

    function closeCreateSubjectDialog() {
        showCreateSubjectDialog.value = false;
        newSubject.name = '';
        newSubject.description = '';
    }

    // edit subject

    function startEditSubject(subject) {
        subject.editing = true;
        subject.editName = subject.name;
        subject.editDescription = subject.description;
    }

    function saveEditSubject(subject) {

        const data = {
            "name": subject.name,
            "description": subject.editDescription
        }

        fetch(
            "http://localhost:5000/api/admin/subject/update/" + subject.id,
            {
                headers: {
                    "Content-Type": "application/json",
                    "Authentication-Token": localStorage.getItem("auth_token") || ""
                },
                method: "PUT",
                body: JSON.stringify(data)
            }
        )
        .then(async response => {
            if (response.ok) {
                subject.name = subject.editName;
                subject.description = subject.editDescription;
                apiError.value = "Subject updated successfully. Reload to view updated dashboard.";
            } else {
                apiError.value = "Failed to update subject.";
            }
        })
        .catch((error) => {
            apiError.value = "Network error: " + error;
        });

        subject.editing = false;
        
        delete subject.editName;
        delete subject.editDescription;
    }

    function cancelEditSubject(subject) {
        subject.editing = false;
        delete subject.editName;
        delete subject.editDescription;
    }

    // delete subject

    function confirmDeleteSubject(subject) {
        fetch(
            "http://localhost:5000/api/admin/subject/delete/" + subject.id,
            {
                headers: {
                    "Content-Type": "application/json",
                    "Authentication-Token": localStorage.getItem("auth_token") || ""
                },
                method: "DELETE"
            }
        )
        .then(async response => {
            if (response.ok) {
                apiError.value = "Subject deleted successfully. Reload to view updated dashboard.";
            } else {
                apiError.value = "Failed to delete subject.";
            }
        })
        .catch((error) => {
            apiError.value = "Network error: " + error;
        })
        .finally(() => {
            showDeleteConfirm.value = false;
            itemToDelete.value = null;
        })
    }
        
    function cancelDelete() { 
        showDeleteConfirm.value = false; 
    }

    // create chapter
    function openCreateChapterDialog(subjectId) {
        showCreateChapterDialog.value = true;
        newChapter.value.subject_id = subjectId;
    }
    function createChapter() {
        if (!newChapter.value.name || !newChapter.value.description) {
            apiError.value = "Please fill in all fields.";
            return;
        }
        fetch("http://localhost:5000/api/admin/chapter/create", {
            headers: {
                "Content-Type": "application/json",
                "Authentication-Token": localStorage.getItem("auth_token") || ""
            },
            method: "POST",
            body: JSON.stringify({
                subject_id: newChapter.value.subject_id,
                name: newChapter.value.name,
                description: newChapter.value.description
            })
        })
        .then(async response => {
            if (response.ok) {
                apiError.value = "Chapter created. Reload to view updated dashboard.";
            } else {
                apiError.value = "Failed to create chapter.";
            }
        })
        .catch(e => { 
            apiError.value = "Network error: " + e; 
        })
        .finally(() => {
            showCreateChapterDialog.value = false;
            newChapter.value = { subject_id: '', name: '', description: '' };
        });
    }

    function closeCreateChapterDialog() {
        showCreateChapterDialog.value = false;
        newChapter.value.subject_id = '';
        newChapter.name = '';
        newChapter.description = '';
    }

    // edit chapter
    function startEditChapter(chapter) {
        chapter.editing = true;
        chapter.editName = chapter.name;
        chapter.editDescription = chapter.description;
    }

    function saveEditChapter(chapter) {
        
        const data = {
            "name": chapter.editName,
            "description": chapter.editDescription
        };
        fetch("http://localhost:5000/api/admin/chapter/update/" + chapter.id, {
            headers: {
                "Content-Type": "application/json",
                "Authentication-Token": localStorage.getItem("auth_token") || ""
            },
            method: "PUT",
            body: JSON.stringify(data)
        })
        .then(async response => {
            if (response.ok) {
                chapter.name = chapter.editName;
                chapter.description = chapter.editDescription;
                apiError.value = "Chapter updated. Reload to view updated dashboard.";
            }
            else apiError.value = "Failed to update chapter.";
        })
        .catch(e => { 
            apiError.value = "Network error: " + e; 
        })
        .finally(() => { 
            chapter.editing = false;
            delete chapter.editName;
            delete chapter.editDescription;
        });
    }

    function cancelEditChapter(chapter) {
        chapter.editing = false;
        delete chapter.editName;
        delete chapter.editDescription;
    }

    // delete chapter

    function confirmDeleteChapter(chapter) {
        fetch(
            "http://localhost:5000/api/admin/chapter/delete/" + chapter.id,
            {
                headers: {
                    "Content-Type": "application/json",
                    "Authentication-Token": localStorage.getItem("auth_token") || ""
                },
                method: "DELETE"
            }
        )
        .then(async response => {
            if (response.ok) {
                apiError.value = "Chapter deleted successfully. Reload to view updated dashboard.";
            } else {
                apiError.value = "Failed to delete chapter.";
            }
        })
        .catch((error) => {
            apiError.value = "Network error: " + error;
        })
        .finally(() => {
            showDeleteConfirm.value = false;
            itemToDelete.value = null;
        })
    }

    // create quiz
    function openCreateQuizDialog(chapterId) {
        showCreateQuizDialog.value = true;
        newQuiz.value.chapter_id = chapterId;
    }
    function createQuiz() {

        if (!newQuiz.value.name || !newQuiz.value.description || !newQuiz.value.date || !newQuiz.value.duration) {
            apiError.value = "Please fill in all fields.";
            return;
        }

        let minutes = newQuiz.value.duration; // integer

        // converting to hours and minutes
        let hours = Math.floor(minutes / 60);
        let mins = minutes % 60;

        // formatting as 'HH:MM', padding with zeros if needed
        let timeDurationStr = `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;

        const data = {
            name: newQuiz.value.name,
            description: newQuiz.value.description,
            chapter_id: newQuiz.value.chapter_id,
            date_of_quiz: newQuiz.value.date + 'T00:00',
            time_duration: timeDurationStr
        }

        console.log(data);

        fetch("http://localhost:5000/api/admin/quiz/create", {
            headers: {
                "Content-Type": "application/json",
                "Authentication-Token": localStorage.getItem("auth_token") || ""
            },
            method: "POST",
            body: JSON.stringify(data)
        })
        .then(async response => {
            if (response.ok) apiError.value = "Quiz created. Reload to view updated dashboard.";
            else apiError.value = "Failed to create quiz.";
        })
        .catch(e => { 
            apiError.value = "Network error: " + e; 
        })
        .finally(() => {
            showCreateQuizDialog.value = false;
            newQuiz.value = { name: '', description: '', chapter_id: '', date: '', duration: '' };
        });
    }

    function closeCreateQuizDialog() {
        showCreateQuizDialog.value = false;
        newQuiz.value = { name: '', description: '', chapter_id: '', date: '', duration: '' };
    }

    // update quiz
    function startEditQuiz(quiz) {
        quiz.editing = true;
        quiz.editName = quiz.name;
        quiz.editDescription = quiz.description;
        quiz.editDate = quiz.date;
        quiz.editDuration = quiz.duration;
    }
    function saveEditQuiz(quiz) {

        let minutes = quiz.editDuration; // integer
        // converting to hours and minutes
        let hours = Math.floor(minutes / 60);
        let mins = minutes % 60;
        // formatting as 'HH:MM', padding with zeros if needed
        let timeDurationStr = `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;

        const data = {
            name: quiz.editName,
            description: quiz.editDescription,
            date_of_quiz: quiz.editDate + 'T00:00',
            time_duration: timeDurationStr
        }

        fetch("http://localhost:5000/api/admin/quiz/update/" + quiz.id, {
            headers: {
                "Content-Type": "application/json",
                "Authentication-Token": localStorage.getItem("auth_token") || ""
            },
            method: "PUT",
            body: JSON.stringify(data)
        })
        .then(async response => {
            if (response.ok) {
                apiError.value = "Quiz updated. Reload to view updated dashboard.";
            } else {
                apiError.value = "Failed to update quiz.";
            }
        })
        .catch(e => { apiError.value = "Network error: " + e; })
        .finally(() => { 
            quiz.editing = false;
        });
    }

    function cancelEditQuiz(quiz) {
        quiz.editing = false;
        delete quiz.editName;
        delete quiz.editDescription;
        delete quiz.editDate;
        delete quiz.editDuration;
    }

    // delete quiz

    function confirmDeleteQuiz(quiz) {
        fetch(
            "http://localhost:5000/api/admin/quiz/delete/" + quiz.id,
            {
                headers: {
                    "Content-Type": "application/json",
                    "Authentication-Token": localStorage.getItem("auth_token") || ""
                },
                method: "DELETE"
            }
        )
        .then(async response => {
            if (response.ok) {
                apiError.value = "Quiz deleted successfully. Reload to view updated dashboard.";
            } else {
                apiError.value = "Failed to delete quiz.";
            }
        })
        .catch((error) => {
            apiError.value = "Network error: " + error;
        })
        .finally(() => {
            showDeleteConfirm.value = false;
            itemToDelete.value = null;
        })
    }

    // create question
    function openCreateQuestionDialog(quizId) {
        showCreateQuestionDialog.value = true;
        newQuestion.value.quiz_id = quizId;
    }

    function createQuestion() {

        if (!newQuestion.value.text || !newQuestion.value.option1 || !newQuestion.value.option2 || 
            !newQuestion.value.option3 || !newQuestion.value.option4 || !newQuestion.value.correct_option) {
            apiError.value = "Please fill in all fields.";
            return;
        }

        const data = {
            question_text: newQuestion.value.text,
            option1: newQuestion.value.option1,
            option2: newQuestion.value.option2,
            option3: newQuestion.value.option3,
            option4: newQuestion.value.option4,
            correct_option: newQuestion.value.correct_option
        }

        console.log(data);

        fetch("http://localhost:5000/api/admin/question/create/" + newQuestion.value.quiz_id, {
            headers: {
                "Content-Type": "application/json",
                "Authentication-Token": localStorage.getItem("auth_token") || ""
            },
            method: "POST",
            body: JSON.stringify(data)
        })
        .then(async response => {
            if (response.ok) {
                apiError.value = "Question created. Reload to view updated dashboard.";
            } else { 
                apiError.value = "Failed to create question.";
            }
        })
        .catch(e => { 
            apiError.value = "Network error: " + e; 
        })
        .finally(() => {
            showCreateQuestionDialog.value = false;
            newQuestion.value = {text: '', option1: '', option2: '', option3: '', option4: '', correct_option: '' };
        });
    }

    function closeCreateQuestionDialog() {
        showCreateQuestionDialog.value = false;
        newQuestion.value = { quiz_id: '', text: '', option1: '', option2: '', option3: '', option4: '', correct_option: '' };
    }

    // update question
    function startEditQuestion(question) {
        question.editing = true;
        question.editText = question.text;
        question.editOption1 = question.option1;
        question.editOption2 = question.option2;
        question.editOption3 = question.option3;
        question.editOption4 = question.option4;
        question.editCorrectOption = question.correct_option;
    }
    function saveEditQuestion(question) {

        const data = {
            text: question.editText,
            option1: question.editOption1,
            option2: question.editOption2,
            option3: question.editOption3,
            option4: question.editOption4,
            correct_option: question.editCorrectOption
        }

        fetch("http://localhost:5000/api/admin/question/update/" + question.id, {
            headers: {
                "Content-Type": "application/json",
                "Authentication-Token": localStorage.getItem("auth_token") || ""
            },
            method: "PUT",
            body: JSON.stringify(data)
        })
        .then(async response => {
            if (response.ok) {
                apiError.value = "Question updated.";
                question.text = question.editText;
                question.option1 = question.editOption1;
                question.option2 = question.editOption2;
                question.option3 = question.editOption3;
                question.option4 = question.editOption4;
                question.correct_option = question.editCorrectOption;
            } else {
                apiError.value = "Failed to update question.";
            }
        })
        .catch(e => { apiError.value = "Network error: " + e; })
        .finally(() => {
            question.editing = false;
            delete question.editText;
            delete question.editOption1;
            delete question.editOption2;
            delete question.editOption3;
            delete question.editOption4;
            delete question.editCorrectOption;
        });
    }

    function cancelEditQuestion(question) {
        question.editing = false;
        delete question.editText;
        delete question.editOption1;
        delete question.editOption2;
        delete question.editOption3;
        delete question.editOption4;
        delete question.editCorrectOption;
    }

    // delete question

    function confirmDeleteQuestion(question) {
        fetch(
            "http://localhost:5000/api/admin/question/delete/" + question.id,
            {
                headers: {
                    "Content-Type": "application/json",
                    "Authentication-Token": localStorage.getItem("auth_token") || ""
                },
                method: "DELETE"
            }
        )
        .then(async response => {
            if (response.ok) {
                apiError.value = "Question deleted successfully. Reload to view updated dashboard.";
            } else {
                apiError.value = "Failed to delete question.";
            }
        })
        .catch((error) => {
            apiError.value = "Network error: " + error;
        })
        .finally(() => {
            showDeleteConfirm.value = false;
            itemToDelete.value = null;
        })
    }

    // delete

    function deleteSubject(subject) {
        showDeleteConfirm.value = true;
        itemToDelete.value = subject.name;
        deleteAction.value = () => confirmDeleteSubject(subject);
    }
    function deleteChapter(chapter) {
        showDeleteConfirm.value = true;
        itemToDelete.value = chapter.name;
        deleteAction.value = () => confirmDeleteChapter(chapter);
    }

    function deleteQuiz(quiz) {
        showDeleteConfirm.value = true;
        itemToDelete.value = quiz.name;
        deleteAction.value = () => confirmDeleteQuiz(quiz);
    }

    function deleteQuestion(question) {
        showDeleteConfirm.value = true;
        itemToDelete.value = question.text;
        deleteAction.value = () => confirmDeleteQuestion(question);
    }

    function confirmDelete() {
        if (deleteAction.value) deleteAction.value();
        deleteAction.value = null;
        showDeleteConfirm.value = false;
        itemToDelete.value = null;
    }

    // create user

    function openCreateUserDialog() {
        showCreateUserDialog.value = true;
    }

    function createUser() {
        if (!newUser.value.username || !newUser.value.email || !newUser.value.password) {
            apiError.value = "Please fill in all fields.";
            return;
        }
        const data = newUser.value;
        fetch(
            "http://localhost:5000/api/admin/user/create",
            {
                headers: {
                    "Content-Type": "application/json",
                    "Authentication-Token": localStorage.getItem("auth_token") || ""
                },
                method: "POST",
                body: JSON.stringify(data)
            }
        )
        .then(async response => {
            if (response.ok) {
                apiError.value = "User created successfully. Reload to view updated dashboard.";
            } else {
                apiError.value = "Failed to create user.";
            }
        })
        .catch((error) => {
            apiError.value = "Network error: " + error;
        })
        .finally(() => {
            showCreateUserDialog.value = false;
            newUser.value = { username: '', email: '', password: '' };
        });
    }

    function closeCreateUserDialog() {
        showCreateUserDialog.value = false;
        newUser.value = { username: '', email: '', password: '' };
    }

    // delete user

    function confirmDeleteUser(user) {
        fetch(
            "http://localhost:5000/api/admin/user/delete/" + user.id,
            {
                headers: {
                    "Content-Type": "application/json",
                    "Authentication-Token": localStorage.getItem("auth_token") || ""
                },
                method: "DELETE"
            }
        )
        .then(async response => {
            if (response.ok) {
                apiError.value = "User deleted successfully. Reload to view updated dashboard.";
            } else {
                apiError.value = "Failed to delete user.";
            }
        })
        .catch((error) => {
            apiError.value = "Network error: " + error;
        })
        .finally(() => {
            showDeleteConfirm.value = false;
            itemToDelete.value = null;
        })
    }

    function deleteUser(user) {
        showDeleteConfirm.value = true;
        itemToDelete.value = user.username;
        deleteAction.value = () => confirmDeleteUser(user);
    }

</script>

<style scoped>

    #admin_dashboard {
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

    .create {
        min-width: 6%;
        padding: 3px 3px;
        background: #000000;
        color: #fff;
        border: none;
        border-radius: 3px;
        font-size: 1.0em;
        font-weight: 500;
        cursor: pointer;
        transition: background 0.2s;
        vertical-align: middle;
    }

    .create:hover {
        background: #0000009f;
    }

    .edit, .delete {
        padding: 3px 3px;
        background: none;
        color: #000000;
        border: none;
        cursor: pointer;
        font-size: 1.0em;
        transition: background 0.2s;
    }

    .save, .cancel {
        padding: 6px 12px;
        color: #000000;
        border: none;
        border-radius: 5px;
        font-size: 0.95em;
        font-weight: 600;
        cursor: pointer;
        transition: background 0.2s;
    }

    .save:hover, .cancel:hover {
        background: #000000;
        color: #fff;
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
        max-width: 350px;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        gap: 14px;
        z-index: 100;
    }

    dialog label {
        font-weight: 500;
        color: #333;
        margin-bottom: 4px;
        display: block;
    }

    dialog input {
        width: 100%;
        margin-top: 4px;
        margin-bottom: 10px;
    }

    dialog button {
        width: 45%;
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

    dialog button:first-of-type{
        margin-right: 10px;
    }

    dialog button:last-of-type {
        margin-left: 10px;
    }

    dialog button:hover {
        background: #fffdfd;
        color: #000000
    }

    .users {
        margin-top: 30px;
        padding: 10px 16px;
        background: #eaf1fb;
        border-radius: 6px;
        text-align: left;
    }

    .users h4 {
        margin-bottom: 10px;
        color: #000000;
        font-size: 1.2em;
        font-weight: 500;
        padding: 6px 10px;
        width: fit-content;
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

    .nav .summary, .logout {
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
        margin-right: 30%;
    }

    .nav .logout {
        margin-left: 30%;
    }


</style>