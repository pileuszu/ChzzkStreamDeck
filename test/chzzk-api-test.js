#!/usr/bin/env node

/**
 * 치지직 API 테스트 스크립트
 * 다양한 방법으로 API 접근 시도
 */

const https = require('https');
const { URL } = require('url');

class ChzzkAPITester {
    constructor() {
        this.testChannelId = '9ae7d38b629b78f48e49fb3106218ff5';
    }

    // 테스트 방법들
    getTestMethods() {
        return [
            {
                name: '기본 User-Agent',
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            },
            {
                name: '완전한 브라우저 헤더',
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Referer': 'https://chzzk.naver.com/',
                    'Origin': 'https://chzzk.naver.com',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-site'
                }
            },
            {
                name: '모바일 User-Agent',
                headers: {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
                }
            },
            {
                name: 'curl 시뮬레이션',
                headers: {
                    'User-Agent': 'curl/8.0.1'
                }
            }
        ];
    }

    // HTTP 요청 실행
    makeRequest(url, headers) {
        return new Promise((resolve, reject) => {
            const parsedUrl = new URL(url);
            
            const options = {
                hostname: parsedUrl.hostname,
                port: parsedUrl.port || 443,
                path: parsedUrl.pathname + parsedUrl.search,
                method: 'GET',
                headers: headers
            };

            const req = https.request(options, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    const result = {
                        statusCode: res.statusCode,
                        success: res.statusCode === 200,
                        rawData: data,
                        jsonData: null,
                        error: null
                    };

                    if (res.statusCode === 200) {
                        try {
                            result.jsonData = JSON.parse(data);
                        } catch (error) {
                            result.success = false;
                            result.error = `JSON 파싱 실패: ${error.message}`;
                        }
                    } else {
                        result.error = `HTTP ${res.statusCode}`;
                        try {
                            const errorData = JSON.parse(data);
                            if (errorData.message) {
                                result.error = `${result.error}: ${errorData.message}`;
                            }
                        } catch (e) {
                            // JSON이 아닌 경우 무시
                        }
                    }

                    resolve(result);
                });
            });

            req.on('error', (error) => {
                reject({
                    success: false,
                    error: `요청 오류: ${error.message}`,
                    statusCode: null,
                    rawData: null,
                    jsonData: null
                });
            });

            req.setTimeout(10000, () => {
                req.destroy();
                reject({
                    success: false,
                    error: '요청 타임아웃',
                    statusCode: null,
                    rawData: null,
                    jsonData: null
                });
            });

            req.end();
        });
    }

    // 모든 방법 테스트
    async testAllMethods() {
        console.log('🎮 치지직 API 테스트 시작');
        console.log('='.repeat(60));
        
        const testUrls = [
            {
                name: '라이브 상태 API',
                url: `https://api.chzzk.naver.com/polling/v1/channels/${this.testChannelId}/live-status`
            },
            {
                name: '채널 정보 API',
                url: `https://api.chzzk.naver.com/service/v1/channels/${this.testChannelId}`
            },
            {
                name: '라이브 상세 API',
                url: `https://api.chzzk.naver.com/service/v1/channels/${this.testChannelId}/live-detail`
            }
        ];

        const methods = this.getTestMethods();
        const results = [];

        for (const urlInfo of testUrls) {
            console.log(`\n📡 ${urlInfo.name} 테스트`);
            console.log(`🔗 ${urlInfo.url}`);
            console.log('-'.repeat(60));
            
            let successFound = false;
            const urlResults = {
                name: urlInfo.name,
                url: urlInfo.url,
                attempts: []
            };

            for (let i = 0; i < methods.length; i++) {
                const method = methods[i];
                console.log(`🔍 ${i + 1}. ${method.name} 시도 중...`);
                
                try {
                    const result = await this.makeRequest(urlInfo.url, method.headers);
                    urlResults.attempts.push({
                        method: method.name,
                        result: result
                    });

                    if (result.success) {
                        console.log(`   ✅ 성공! (HTTP ${result.statusCode})`);
                        if (result.jsonData && result.jsonData.content) {
                            const content = result.jsonData.content;
                            if (content.channelName) {
                                console.log(`   📺 채널명: ${content.channelName}`);
                            }
                            if (content.status) {
                                console.log(`   📊 상태: ${content.status}`);
                            }
                            if (content.chatChannelId) {
                                console.log(`   💬 채팅 채널 ID: ${content.chatChannelId}`);
                            }
                        }
                        successFound = true;
                        break;
                    } else {
                        console.log(`   ❌ 실패: ${result.error}`);
                    }
                } catch (error) {
                    console.log(`   ❌ 예외: ${error.error || error.message}`);
                    urlResults.attempts.push({
                        method: method.name,
                        result: { success: false, error: error.error || error.message }
                    });
                }
            }

            if (!successFound) {
                console.log(`   🚫 모든 방법 실패`);
            }

            results.push(urlResults);
        }

        // 최종 요약
        this.printSummary(results);
    }

    // 결과 요약 출력
    printSummary(results) {
        console.log('\n📋 테스트 결과 요약');
        console.log('='.repeat(60));
        
        const successfulEndpoints = [];
        const failedEndpoints = [];

        for (const result of results) {
            const hasSuccess = result.attempts.some(attempt => attempt.result.success);
            
            if (hasSuccess) {
                const successfulAttempt = result.attempts.find(attempt => attempt.result.success);
                successfulEndpoints.push({
                    name: result.name,
                    method: successfulAttempt.method,
                    url: result.url
                });
            } else {
                failedEndpoints.push({
                    name: result.name,
                    url: result.url,
                    errors: result.attempts.map(a => a.result.error).join(', ')
                });
            }
        }

        // 성공한 엔드포인트들
        if (successfulEndpoints.length > 0) {
            console.log('\n✅ 성공한 API 엔드포인트:');
            successfulEndpoints.forEach((endpoint, index) => {
                console.log(`${index + 1}. ${endpoint.name}`);
                console.log(`   🔧 성공 방법: ${endpoint.method}`);
                console.log(`   🔗 URL: ${endpoint.url}`);
                console.log('');
            });
        }

        // 실패한 엔드포인트들
        if (failedEndpoints.length > 0) {
            console.log('\n❌ 실패한 API 엔드포인트:');
            failedEndpoints.forEach((endpoint, index) => {
                console.log(`${index + 1}. ${endpoint.name}`);
                console.log(`   🚫 오류: ${endpoint.errors}`);
                console.log(`   🔗 URL: ${endpoint.url}`);
                console.log('');
            });
        }

        // 전체 결과
        console.log(`📊 전체 결과: ${successfulEndpoints.length}/${results.length} 성공`);
        
        if (successfulEndpoints.length > 0) {
            console.log('\n🎉 일부 API가 성공했습니다! 채팅 테스트를 진행할 수 있습니다.');
            console.log(`💡 명령어: npm run chat-test ${this.testChannelId}`);
        } else {
            console.log('\n🚫 모든 API가 실패했습니다.');
            console.log('💡 해결 방법:');
            console.log('   1. 다른 채널 ID로 시도해보세요');
            console.log('   2. 현재 라이브 방송 중인 채널을 사용하세요');
            console.log('   3. 잠시 후 다시 시도해보세요');
        }
        
        console.log('\n🏁 테스트 완료');
    }
}

// 프로그램 실행
async function main() {
    const channelId = process.argv[2];
    
    if (!channelId) {
        console.log('🎮 치지직 API 연결 테스트');
        console.log('='.repeat(60));
        console.log('');
        console.log('사용법: node test/chzzk-api-test.js [채널ID]');
        console.log('또는:   npm run api-test [채널ID]');
        console.log('');
        console.log('예시: npm run api-test 9ae7d38b629b78f48e49fb3106218ff5');
        console.log('');
        console.log('💡 채널 ID 찾는 방법:');
        console.log('   1. 치지직 방송 페이지 접속');
        console.log('   2. URL에서 /live/ 뒤의 32자리 ID 복사');
        console.log('   3. 예: https://chzzk.naver.com/live/9ae7d38b629b78f48e49fb3106218ff5');
        process.exit(1);
    }
    
    const tester = new ChzzkAPITester();
    tester.testChannelId = channelId;
    
    console.log(`📺 테스트 채널 ID: ${channelId}`);
    await tester.testAllMethods();
}

if (require.main === module) {
    main().catch(console.error);
} 