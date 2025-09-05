<!-- root component of application, acting as a container for other components and serving as the main template -->

<template>
  <div id = "app">
    <h1> Quiz Master </h1>
    <router-view/>
  </div>
</template>

<script setup>

</script>

<style>
#app {
  font-family: serif;
  text-align: center;
  margin-top: 40px;
}
</style>
