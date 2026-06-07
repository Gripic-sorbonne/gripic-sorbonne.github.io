import { graphql } from "gatsby"
import * as React from 'react'
import Layout from '../components/layout'
import "../style/accueil.css"

const ProgrammesLayout = ({ data }) => {
    const nodes = data.allMarkdownRemark.nodes.filter(n => !n.fields.slug.startsWith('_'))

    return (
        <Layout nodes={nodes}>
            {(toggleTag, tags, search) => {
                return (
                    <div id="programmes-container">
                        {nodes.map(node => (
                            <div key={node.frontmatter.uuid} className="programme-item">
                                <h2>{node.frontmatter.title}</h2>
                                <div dangerouslySetInnerHTML={{ __html: node.html }} />
                            </div>
                        ))}
                    </div>
                )
            }}
        </Layout>
    )
}

export const query = graphql`
    query ProgrammesQuery($pageName: String = "") {
        allMarkdownRemark(
            sort: {fields: {date: DESC}},
            filter: {fields: {collection: {eq: $pageName}}}
            limit: 999
        ) {
            nodes {
                html
                frontmatter {
                    tags
                    title
                    uuid
                }
                fields {
                    collection
                    date(formatString: "DD MMMM, YYYY", locale: "fr")
                    slug
                }
            }
        }
    }
`

export default ProgrammesLayout
