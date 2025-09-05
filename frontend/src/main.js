// entry point of application, enabling vue initialization and configuration of plugins or additional libraries

import { createApp } from 'vue'
import app from './app.vue'
import router from './router.js'
import 'bootstrap-icons/font/bootstrap-icons.css';

const app_ = createApp(app);
app_.use(router);
app_.mount('#app');