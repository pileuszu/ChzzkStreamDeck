#!/usr/bin/env node

/**
 * 치지직 채널 정보 API 전체 응답 확인 도구
 * 성공한 API 엔드포인트의 모든 데이터를 상세히 출력
 */

const https = require('https');
const { URL } = require('url');

class ChzzkChannelInfoViewer {
    constructor() {
        this.defaultChannels = [
            '789d1d9c5b58c847f9f18c8e5073c580', // 아우슈
            '9ae7d38b629b78f48e49fb3106218ff5', // 예시 채널
        ];
    }

    // HTTP 요청 실행
    makeRequest(url) {
        return new Promise((resolve, reject) => {
            const parsedUrl = new URL(url);
            
            const options = {
                hostname: parsedUrl.hostname,
                port: parsedUrl.port || 443,
                path: parsedUrl.pathname + parsedUrl.search,
                method: 'GET',
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
                    'Connection': 'keep-alive',
                    'Referer': 'https://chzzk.naver.com/'
                }
            };

            const req = https.request(options, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    const result = {
                        statusCode: res.statusCode,
                        headers: res.headers,
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

    // 채널 정보 가져오기 및 출력
    async fetchAndDisplayChannelInfo(channelId) {
        console.log(`\n📡 채널 정보 조회 중...`);
        console.log(`🆔 채널 ID: ${channelId}`);
        console.log('='.repeat(80));

        const url = `https://api.chzzk.naver.com/service/v1/channels/${channelId}`;
        console.log(`🔗 API URL: ${url}`);

        try {
            const result = await this.makeRequest(url);

            if (result.success && result.jsonData) {
                this.displaySuccessResult(result.jsonData);
            } else {
                this.displayErrorResult(result);
            }

        } catch (error) {
            console.log(`\n❌ 요청 실패: ${error.error || error.message}`);
        }
    }

    // 성공 결과 출력
    displaySuccessResult(data) {
        console.log(`\n✅ API 호출 성공!`);
        console.log('━'.repeat(80));

        // 기본 응답 구조
        console.log(`📋 응답 코드: ${data.code || 'N/A'}`);
        console.log(`📋 응답 메시지: ${data.message || 'null'}`);

        if (data.content) {
            this.displayChannelContent(data.content);
        }

        // 전체 JSON 원본 데이터
        console.log(`\n📄 전체 JSON 응답 데이터:`);
        console.log('━'.repeat(80));
        console.log(JSON.stringify(data, null, 2));
        console.log('━'.repeat(80));
    }

    // 채널 콘텐츠 정보 출력
    displayChannelContent(content) {
        console.log(`\n📺 채널 기본 정보:`);
        console.log('-'.repeat(50));
        console.log(`🆔 채널 ID: ${content.channelId || 'N/A'}`);
        console.log(`📛 채널명: ${content.channelName || 'N/A'}`);
        console.log(`🖼️  채널 이미지: ${content.channelImageUrl || '없음'}`);
        console.log(`✅ 인증 마크: ${content.verifiedMark ? '있음' : '없음'}`);
        console.log(`📺 채널 타입: ${content.channelType || 'N/A'}`);
        console.log(`📝 채널 설명: ${content.channelDescription || '없음'}`);

        console.log(`\n📊 채널 통계:`);
        console.log('-'.repeat(50));
        console.log(`👥 팔로워 수: ${content.followerCount?.toLocaleString() || 'N/A'}명`);
        console.log(`📺 라이브 오픈: ${content.openLive ? '허용' : '비허용'}`);
        console.log(`💬 팔로워 채팅: ${content.subscriptionAvailability ? '가능' : '불가능'}`);
        console.log(`🎥 VOD 게시: ${content.subscriptionPaymentAvailability ? '가능' : '불가능'}`);

        if (content.personalData) {
            console.log(`\n👤 개인 데이터:`);
            console.log('-'.repeat(50));
            console.log(`🔔 팔로우 상태: ${content.personalData.following ? '팔로잉' : '미팔로잉'}`);
            console.log(`🔕 알림 설정: ${content.personalData.notification ? '켜짐' : '꺼짐'}`);
            console.log(`💰 구독 상태: ${content.personalData.subscription ? '구독중' : '미구독'}`);
        }

        if (content.subscription) {
            console.log(`\n💳 구독 정보:`);
            console.log('-'.repeat(50));
            console.log(`💰 구독료: ${content.subscription.subscriptionPrice || 'N/A'}원`);
            console.log(`🔒 구독 전용: ${content.subscription.subscriptionOnlyPlaymode || 'N/A'}`);
            console.log(`📝 구독 설명: ${content.subscription.subscriptionDescription || '없음'}`);
        }

        // 활동 정보
        if (content.activityInfo) {
            console.log(`\n📈 활동 정보:`);
            console.log('-'.repeat(50));
            console.log(`🎮 게임: ${content.activityInfo.game || '없음'}`);
            console.log(`🎯 카테고리: ${content.activityInfo.category || '없음'}`);
            console.log(`📊 활동 점수: ${content.activityInfo.activityScore || 'N/A'}`);
        }

        // 라이브 정보
        if (content.liveInfo) {
            console.log(`\n🔴 라이브 정보:`);
            console.log('-'.repeat(50));
            console.log(`📺 상태: ${content.liveInfo.status || 'N/A'}`);
            console.log(`🏷️  제목: ${content.liveInfo.liveTitle || '없음'}`);
            console.log(`🖼️  썸네일: ${content.liveInfo.liveThumbnailImageUrl || '없음'}`);
            console.log(`👥 시청자 수: ${content.liveInfo.concurrentUserCount?.toLocaleString() || 'N/A'}명`);
            console.log(`⏰ 시작 시간: ${content.liveInfo.openDate ? new Date(content.liveInfo.openDate).toLocaleString('ko-KR') : 'N/A'}`);
        }

        // 기타 모든 필드들
        console.log(`\n🔍 기타 정보:`);
        console.log('-'.repeat(50));
        const excludeFields = ['channelId', 'channelName', 'channelImageUrl', 'verifiedMark', 
                              'channelType', 'channelDescription', 'followerCount', 'openLive', 
                              'subscriptionAvailability', 'subscriptionPaymentAvailability',
                              'personalData', 'subscription', 'activityInfo', 'liveInfo'];
        
        Object.keys(content).forEach(key => {
            if (!excludeFields.includes(key)) {
                const value = content[key];
                if (value !== null && value !== undefined) {
                    console.log(`${key}: ${typeof value === 'object' ? JSON.stringify(value) : value}`);
                }
            }
        });
    }

    // 오류 결과 출력
    displayErrorResult(result) {
        console.log(`\n❌ API 호출 실패`);
        console.log('━'.repeat(80));
        console.log(`📋 HTTP 상태 코드: ${result.statusCode || 'N/A'}`);
        console.log(`📋 오류 메시지: ${result.error || 'N/A'}`);
        
        if (result.rawData) {
            console.log(`\n📄 원시 응답 데이터:`);
            console.log('-'.repeat(50));
            console.log(result.rawData);
        }
    }

    // 여러 채널 테스트
    async testMultipleChannels(channelIds) {
        console.log('🎮 치지직 채널 정보 조회 도구');
        console.log('='.repeat(80));
        console.log(`📊 총 ${channelIds.length}개 채널 테스트 예정`);

        for (let i = 0; i < channelIds.length; i++) {
            const channelId = channelIds[i];
            console.log(`\n[${i + 1}/${channelIds.length}] 채널 테스트`);
            await this.fetchAndDisplayChannelInfo(channelId);
            
            if (i < channelIds.length - 1) {
                console.log(`\n${'─'.repeat(80)}`);
                console.log('⏳ 2초 후 다음 채널 테스트...');
                await new Promise(resolve => setTimeout(resolve, 2000));
            }
        }

        console.log(`\n🏁 모든 채널 테스트 완료!`);
    }
}

// 메인 실행 함수
async function main() {
    const channelId = process.argv[2];
    const viewer = new ChzzkChannelInfoViewer();

    if (!channelId) {
        console.log('🎮 치지직 채널 정보 조회 도구');
        console.log('='.repeat(80));
        console.log('');
        console.log('사용법: node test/chzzk-channel-info.js [채널ID]');
        console.log('또는:   npm run channel-info [채널ID]');
        console.log('');
        console.log('예시:');
        console.log('  npm run channel-info 789d1d9c5b58c847f9f18c8e5073c580');
        console.log('  npm run channel-info 9ae7d38b629b78f48e49fb3106218ff5');
        console.log('');
        console.log('💡 또는 기본 채널들을 모두 테스트:');
        console.log('  node test/chzzk-channel-info.js --all');
        console.log('');
        console.log('💡 채널 ID 찾는 방법:');
        console.log('   1. 치지직 방송 페이지 접속');
        console.log('   2. URL에서 /live/ 뒤의 32자리 ID 복사');
        console.log('   3. 예: https://chzzk.naver.com/live/789d1d9c5b58c847f9f18c8e5073c580');
        process.exit(1);
    }

    if (channelId === '--all') {
        await viewer.testMultipleChannels(viewer.defaultChannels);
    } else {
        await viewer.fetchAndDisplayChannelInfo(channelId);
    }
}

if (require.main === module) {
    main().catch(error => {
        console.error('프로그램 실행 오류:', error.message);
        process.exit(1);
    });
} 