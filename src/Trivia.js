import React,{useState} from "react";
import confetti from "canvas-confetti";

const API_URL="https://sportsfan360-ai-agent-1.onrender.com";

function Trivia(){

const [questions,setQuestions]=useState([]);
const [quizStarted,setQuizStarted]=useState(false);
const [current,setCurrent]=useState(0);
const [score,setScore]=useState(0);
const [selected,setSelected]=useState(null);
const [quizFinished,setQuizFinished]=useState(false);
const [loading,setLoading]=useState(false);


/* FETCH QUESTIONS */

const startQuiz=async()=>{

setLoading(true);

try{

const res=await fetch(`${API_URL}/trivia`);
const data=await res.json();

setQuestions(data.questions || []);
setQuizStarted(true);
setCurrent(0);
setScore(0);
setSelected(null);
setQuizFinished(false);

}catch(e){

console.error("Trivia load error",e);

}

setLoading(false);

};


/* ANSWER SELECT */

const selectAnswer=(opt)=>{

setSelected(opt);

if(opt===questions[current].answer){
setScore(prev=>prev+1);
}

};


/* NEXT QUESTION */

const nextQuestion=()=>{

setSelected(null);

if(current+1<questions.length){

setCurrent(prev=>prev+1);

}else{

setQuizFinished(true);

/* CONFETTI FOR GOOD SCORE */

if(score>=7){

confetti({
particleCount:120,
spread:80,
origin:{y:0.6}
});

}

}

};


/* RESET */

const resetQuiz=()=>{

setQuizStarted(false);
setQuizFinished(false);
setCurrent(0);
setScore(0);
setSelected(null);
setQuestions([]);

};


/* ===================== UI ===================== */

return(

<div className="trivia">

{/* START SCREEN */}

{!quizStarted && (

<div className="quizStart">

<h2>🏏 IPL Trivia Challenge</h2>

<p>Answer 10 questions and test your IPL knowledge!</p>

{loading ? (

<p>Loading questions...</p>

) : (

<button className="startQuiz" onClick={startQuiz}>
Start Quiz
</button>

)}

</div>

)}


{/* QUIZ SCREEN */}

{quizStarted && !quizFinished && questions.length>0 && (

<div className="quizCard">

<div className="progressBar">
<div style={{width:`${((current+1)/questions.length)*100}%`}}></div>
</div>

<h3>
Question {current+1} / {questions.length}
</h3>

<p className="quizQuestion">
{questions[current].q}
</p>

<div className="quizOptions">

{questions[current].options.map((opt,i)=>{

let className="quizOption";

if(selected){

if(opt===questions[current].answer){
className+=" correct";
}
else if(opt===selected){
className+=" wrong";
}

}

return(

<button
key={i}
className={className}
onClick={()=>selectAnswer(opt)}
disabled={selected}
>
{opt}
</button>

);

})}

</div>

{selected && (

<button className="nextBtn" onClick={nextQuestion}>
Next →
</button>

)}

</div>

)}


{/* RESULT SCREEN */}

{quizFinished && (

<div className="quizResult">

<h2>🏏 IPL Trivia Complete</h2>

<h3>
Your Score: {score} / {questions.length}
</h3>

{score===questions.length && <p>🏆 Perfect Score! IPL Master!</p>}
{score>=8 && score<questions.length && <p>🔥 IPL Expert!</p>}
{score>=5 && score<8 && <p>👏 Good Knowledge!</p>}
{score<5 && <p>🙂 Better luck next time!</p>}

<button className="startQuiz" onClick={resetQuiz}>
Play Again
</button>

</div>

)}

</div>

);
}

export default Trivia;