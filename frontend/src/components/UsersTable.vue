<template>
    <div class="container">
      <h1>Users List</h1>
      <button @click="fetchUsers" class="fetch-button">Fetch Users</button>
  
      <table v-if="users.length > 0">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Age</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.name || 'N/A' }}</td>
            <td>{{ user.email || 'N/A' }}</td>
            <td>{{ user.age !== null ? user.age : 'N/A' }}</td>
          </tr>
        </tbody>
      </table>
  
      <p v-if="users.length === 0">Click "Fetch Users" to load data.</p>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  
  export default {
    data() {
      return {
        users: [],
      };
    },
    methods: {
      async fetchUsers() {
        try {
          const response = await axios.get(
            "https://rekehtm1f0.execute-api.us-east-1.amazonaws.com/dev/api/users/"
          );
          console.log("API Response:", response.data);
          this.users = response.data.users || [];
        } catch (error) {
          console.error("Error fetching users:", error);
        }
      },
    },
  };
  </script>
  
  <style>
  .container {
    text-align: center;
    margin-top: 20px;
  }
  .fetch-button {
    padding: 10px 20px;
    font-size: 16px;
    margin-bottom: 20px;
    cursor: pointer;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
  }
  .fetch-button:hover {
    background-color: #0056b3;
  }
  table {
    margin: 0 auto;
    border-collapse: collapse;
    width: 80%;
    border: 1px solid #ddd;
  }
  th, td {
    padding: 10px;
    text-align: left;
    border-bottom: 1px solid #ddd;
  }
  th {
    background-color: #f4f4f4;
  }
  </style>
  