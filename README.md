# 🍡 경단 FastAPI 레포지토리

> AI 기반 경제 지식 플랫폼의 기술적 개요

경단 FastAPI 레포지토리는 경제 기사의 재생성, 데이터 인사이트 제공, 추천 시스템 등을 포함한 인공지능 기술을 다룹니다.

### 주요 기술 스택
- `LLM (Large Language Models)`
- `RAG (Retrieval-Augmented Generation)`, `LangChain`, `Chroma`
- `Morpheme Analyzer`, `TF-IDF`
- `LightFM`
- `plotly`

## 📋 목차

1. [RAG 도입](#-rag-도입)
   - [도입 이유](#도입-이유)
   - [프로세스](#프로세스)
   - [기술 구성](#기술-구성)
   - [활용 모듈](#활용-모듈)
   - [대규모 벡터 데이터베이스](#대규모-벡터-데이터베이스)
2. [기능별 기술 구성](#-기능별-기술-구성)
   - [기사 재생성](#-기사-재생성)
   - [데이터 인사이트](#-데이터-인사이트)
   - [챗봇](#-챗봇)
   - [추천 시스템](#-추천-시스템)
3. [활용 데이터](#-활용-데이터)

## 🤖 RAG 도입

### 도입 이유

- **사실 관계 오류와 맥락 이해의 한계**를 개선하기 위해 도입
- 최신 정보와 정확한 사실 관계 필요
- **생성물의 품질과 공정성 보장** 및 **인간-AI 협업 방식 정립** 등 해결 과제 대응
- 생성 AI 기술의 혜택을 **안전하고 효과적으로 제공**하기 위한 방법 모색

### 프로세스

1. **질문 인코딩**: 사용자의 질문을 벡터 형태로 변환
2. **지식 검색**: 외부 지식 베이스(Wikipedia, 뉴스 기사 등)에서 관련 정보 검색
3. **답변 생성**: 검색된 지식을 이용해 답변 생성

### 기술 구성

- **질의 인코더(Query Encoder)**: 질문을 벡터 형태로 인코딩
- **지식 검색기(Knowledge Retriever)**: 외부 지식 베이스에서 정보 검색
- **지식 증강 생성기(Knowledge-Augmented Generator)**: 검색된 정보를 바탕으로 답변 생성

### 활용 모듈

- **LangChain**: 검색 추론 능력 향상
- **Google Custom Search Engine**: 웹 결과 검색
- **WikiPedia Retriever**: Wikipedia에서 정보 검색

### 대규모 벡터 데이터베이스

### 도입 이유

- 복잡도가 낮고 처음 사용하기에 **Chroma** 선택

### 기술 구성

- **Chroma**: 텍스트를 벡터로 변환하여 의미론적 유사성 기반 검색
- **LangChain**: 검색 추론 능력 향상

### 예시

1. **질문 입력**: 사용자가 질문 입력
2. **Google 검색**: Google Custom Search API로 결과 검색
3. **벡터화 및 저장**: 검색 결과를 텍스트 임베딩으로 변환 후 ChromaDB에 저장
4. **검색 수행**: ChromaDB로 유사한 문서 검색
5. **LLM 분석 및 정보 통합**: LangChain으로 문서 분석 및 정보 통합

---

## 🔧 기능별 기술 구성

### 📰 기사 재생성

- **RAG**: 최신 정보 검색 및 데이터의 정확도와 신뢰성 향상
- **NLP 모델**: 자연어처리 모델을 통해 기사 재작성

### 📊 데이터 인사이트

- **데이터 시각화 도구**: 대화형 인포그래픽을 통해 공공 데이터를 시각화
- **추론 예시**: "한국에서 가장 삼겹살이 비싼 곳은 어디인가?" 등 데이터 시각화

### 🤖 챗봇

- **TF-IDF**: 문서 간 유사도 계산
- **형태소 분석기**: 한국어 텍스트 분석을 위한 형태소 분석

### 💡 추천 시스템

- **LightFM**: 협업 필터링과 콘텐츠 기반 필터링을 결합한 추천 알고리즘
- **사용자 선호도 분석**: 사용자 행동 데이터를 기반으로 맞춤형 추천 제공

---

## 📚 활용 데이터

- **공공데이터포털**
- **매경 홈페이지**
- **한국은행**
- **Google Custom Search Engine**
- **Naver Map API**
