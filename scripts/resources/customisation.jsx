import * as React from 'react'
import LogoSorbonne from '../images/logo_gripic.png'

export const Introduction = () => { return (
    <div className="landing-block text">
        <h2>Template de site académique de la Fac de Lettres</h2>
        <p>
            Ce site est un modèle pour les sites de laboratoire de <a href="https://lettres.sorbonne-universite.fr/">Faculté des Lettres de Sorbonne Université</a>.
                Il a pour vocation d'être un exemple modifiable afin de mettre en place aisément des sites web permettant de publier billets de blogs et mettre en avant des événements liés à l'activité d'un laboratoire.
        </p>
        <p>
            Fonctionnalités principales
            <ul>
                <li> Publier du contenu à partir de simples fichiers markdown </li>
                <li> Mise en avant d'événements </li>
                <li> Gestion facilitée de membres </li>
            </ul>
        </p>
        <p>
            Ce template a été créé par les ingénieurs de <a href="ceres.sorbonne-universite.fr">l'unité de service du CERES</a>.
        </p>
    </div>
)}

export const Footer = () => (
    <footer id="footer">
        <div className="footer-block">
            <p><strong>GRIPIC</strong> — Groupe de recherche sur les enjeux de la communication</p>
            <p>CELSA Sorbonne Université</p>
            <div style={{ marginTop: "1rem" }}>
                <a href='https://lettres.sorbonne-universite.fr/' style={{ display: "inline-block", textDecoration: "none" }}>
                    <img 
                        src={LogoSorbonne} 
                        alt="Sorbonne Université" 
                        draggable={false}
                        style={{ width: "160px", height: "auto", maxWidth: "100%", margin: 0, display: "block", objectFit: "contain" }} 
                    />
                </a>
            </div>
        </div>
        <div className="footer-block">
            <p><strong>Pour nous rendre visite :</strong> 77, rue de Villiers, 92200 Neuilly-sur-Seine.</p>
            <p>Métro : "Pont de Levallois-Bécon" (ligne 3) ou "Pont-de-Neuilly" (ligne 1)</p>
            <p><strong>Pour nous contacter :</strong> <a href="mailto:contact@gripic.fr">contact@gripic.fr</a></p>
        </div>
    </footer>
)