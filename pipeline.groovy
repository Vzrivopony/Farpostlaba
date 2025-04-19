pipeline {
    agent any
    
    environment {
        DB_URL = "jdbc:mysql://mysql:3306/mydb?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC"
        DB_USER = "root"
        DB_PASSWORD = "root"
        OUTPUT_CSV = "result.csv"
    }
    
    stages {
        stage('Extract') {
            steps {
                script {
                    def results = queryDatabase()
                    writeFile file: 'raw_data.json', text: groovy.json.JsonOutput.toJson(results)
                    echo "✅ Данные извлечены (${results.size()} записей)"
                }
            }
        }
        
        stage('Transform') {
            steps {
                script {
                    try {
                        def rawData = readJSON file: 'raw_data.json'
                        def processedData = transformData(rawData)
                        writeFile file: 'processed_data.json', text: groovy.json.JsonOutput.toJson(processedData)
                        echo "✅ Данные преобразованы"
                    } catch (Exception e) {
                        error "❌ Transform failed: ${e.getMessage()}"
                    }
                }
            }
        }
        
        stage('Load') {
            steps {
                script {
                    try {
                        def processedData = readJSON file: 'processed_data.json'
                        generateCSV(processedData, env.OUTPUT_CSV)
                        archiveArtifacts artifacts: env.OUTPUT_CSV
                        echo "✅ Результат сохранен в ${env.OUTPUT_CSV}"
                    } catch (Exception e) {
                        error "❌ Load failed: ${e.getMessage()}"
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo "🏁 Pipeline завершен. Статус: ${currentBuild.currentResult}"
        }
    }
}

@NonCPS
def queryDatabase() {
    def results = []
    
    try {
        Class.forName('com.mysql.cj.jdbc.Driver')
        def sql = groovy.sql.Sql.newInstance(
            env.DB_URL,
            env.DB_USER,
            env.DB_PASSWORD,
            "com.mysql.cj.jdbc.Driver"
        )
        
        sql.eachRow("""
            SELECT 
                DATE(a.action_time) as day,
                COUNT(DISTINCT CASE WHEN at.name = 'create_account' THEN a.users_id END) as new_accounts,
                COUNT(DISTINCT CASE WHEN at.name = 'create_comment' THEN a.comments_id END) as total_messages,
                COUNT(DISTINCT CASE WHEN at.name = 'create_comment' AND a.users_id IS NULL THEN a.comments_id END) as anonymous_messages,
                COUNT(DISTINCT CASE WHEN at.name = 'create_thread' THEN a.threads_id END) as total_threads
            FROM actions a
            JOIN actions_type at ON a.actions_type_id = at.id
            GROUP BY DATE(a.action_time)
            ORDER BY day
        """) { row ->
            results.add([
                day: row.day.toString(),
                new_accounts: row.new_accounts,
                total_messages: row.total_messages,
                anonymous_messages: row.anonymous_messages,
                total_threads: row.total_threads
            ])
        }
        
        sql.close()
    } catch (Exception e) {
        error "❌ Database query failed: ${e.getMessage()}"
    }
    
    return results
}

@NonCPS
def transformData(rawData) {
    def processedData = []
    
    rawData.eachWithIndex { row, index ->
        def prevThreads = index > 0 ? rawData[index-1].total_threads : row.total_threads
        def threadGrowth = prevThreads > 0 ? 
            ((row.total_threads - prevThreads) / prevThreads * 100).setScale(2, java.math.RoundingMode.HALF_UP) : 0
        
        def anonymousPercent = row.total_messages > 0 ? 
            (row.anonymous_messages / row.total_messages * 100).setScale(2, java.math.RoundingMode.HALF_UP) : 0
        
        processedData.add([
            date: row.day,
            new_accounts: row.new_accounts,
            total_messages: row.total_messages,
            anonymous_percent: anonymousPercent,
            thread_growth: threadGrowth
        ])
    }
    
    return processedData
}

@NonCPS
def generateCSV(data, filename) {
    def csvLines = ["Дата;Новые аккаунты;Сообщения;% анонимных;Прирост тем(%)"]
    
    data.each { row ->
        csvLines.add("${row.date};${row.new_accounts};${row.total_messages};${row.anonymous_percent};${row.thread_growth}")
    }
    
    writeFile file: filename, text: csvLines.join("\n")
}