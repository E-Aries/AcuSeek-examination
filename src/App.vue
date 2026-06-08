<!-- Author: 达咩 | 轻则 -->

﻿<template>
  <router-view />
</template>

<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

onMounted(() => {
  const token = localStorage.getItem("token");
  if (!token && router.currentRoute.value.name !== "Login") {
    router.push({ name: "Login" });
  }
});
</script>

<style>
.app-root {
  min-height: 100vh;
}
</style>
