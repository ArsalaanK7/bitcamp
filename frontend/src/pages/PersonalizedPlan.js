import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Paper, CircularProgress } from '@mui/material';
import axios from 'axios';

const PersonalizedPlan = () => {
  const [tasks, setTasks] = useState('');
  const [plan, setPlan] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post('http://localhost:5000/generate-plan', {
        tasks: tasks.split(',').map(task => task.trim()),
      });
      
      setPlan(response.data.plan);
    } catch (err) {
      setError('Failed to generate plan. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Personalized Daily Plan
      </Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="body1" gutterBottom>
          Enter the tasks you'd like to complete today (comma-separated):
        </Typography>
        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            multiline
            rows={4}
            value={tasks}
            onChange={(e) => setTasks(e.target.value)}
            placeholder="e.g., homework, exercise, meal prepping"
            variant="outlined"
            sx={{ mb: 2 }}
          />
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading || !tasks.trim()}
          >
            {loading ? <CircularProgress size={24} /> : 'Generate Plan'}
          </Button>
        </form>
      </Paper>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      {plan && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Your Personalized Plan
          </Typography>
          <Typography variant="body1" style={{ whiteSpace: 'pre-line' }}>
            {plan}
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default PersonalizedPlan; 