import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

import {useState} from "react";

function App(){
    //state(état ou données)
    const [i,setI]=useState(5);

    //comportement


    //affichage (render)
    return <div id="root">{i}</div>
}

export default App;












const zoneSurvol = document.getElementById('zoneSurvol');

// Quand la souris entre dans la zone
zoneSurvol.addEventListener('mouseover', function() {
  zoneSurvol.style.backgroundColor = 'yellow';
});

// Quand la souris quitte la zone
zoneSurvol.addEventListener('mouseout', function() {
  zoneSurvol.style.backgroundColor = '';
});
