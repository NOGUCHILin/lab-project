/**
 * Detailed service documentation and usage information
 * 各サービスの詳細な使い方と機能説明
 */

export interface ServiceDetail {
  id: string;
  quickStart: {
    title: string;
    steps: Array<{
      step: number;
      title: string;
      description: string;
      tip?: string;
      command?: string;
    }>;
  };
  features: Array<{
    name: string;
    description: string;
    howToUse: string;
    example?: string;
    icon?: string;
  }>;
  useCases: Array<{
    title: string;
    scenario: string;
    steps: string[];
    benefits?: string[];
  }>;
  faq: Array<{
    question: string;
    answer: string;
    category?: string;
  }>;
  troubleshooting: Array<{
    issue: string;
    solution: string;
    relatedError?: string;
    preventiveMeasure?: string;
  }>;
  shortcuts?: Array<{
    keys: string;
    action: string;
    context?: string;
  }>;
  apiEndpoints?: Array<{
    method: string;
    endpoint: string;
    description: string;
    example?: string;
    auth?: boolean;
  }>;
  configuration?: {
    files?: string[];
    environmentVariables?: Array<{
      name: string;
      description: string;
      example: string;
    }>;
    ports?: Array<{
      port: number;
      protocol: string;
      description: string;
    }>;
  };
  integrations?: Array<{
    service: string;
    description: string;
    howTo: string;
  }>;
  resources: Array<{
    type: 'doc' | 'video' | 'tutorial' | 'github' | 'community';
    title: string;
    url: string;
    language?: 'ja' | 'en';
  }>;
}

export const SERVICE_DETAILS: Record<string, ServiceDetail> = {
  'code-server': {
    id: 'code-server',
    quickStart: {
      title: 'Code Serverを始める',
      steps: [
        {
          step: 1,
          title: 'アクセス',
          description: 'ブラウザで「サービスを開く」ボタンをクリックしてCode Serverにアクセスします',
          tip: '初回アクセス時は数秒かかる場合があります'
        },
        {
          step: 2,
          title: 'ワークスペースを開く',
          description: 'File > Open Folder から編集したいプロジェクトフォルダを選択',
          tip: '/home/noguchilin/projects/ 配下がメインの作業ディレクトリです',
          command: 'Ctrl+K → Ctrl+O'
        },
        {
          step: 3,
          title: 'コーディング開始',
          description: 'デスクトップ版VSCodeと同じようにファイル編集、ターミナル操作が可能',
          tip: 'Ctrl+Shift+P でコマンドパレットを開けます'
        }
      ]
    },
    features: [
      {
        name: '統合ターミナル',
        description: 'VSCode内蔵のターミナルでコマンド実行が可能',
        howToUse: 'Ctrl+` でターミナルを開く。複数のターミナルセッションも管理可能',
        example: 'npm install, git commit, docker runなどのコマンドを直接実行',
        icon: '🖥️'
      },
      {
        name: '拡張機能',
        description: 'VSCode Marketplaceから拡張機能をインストール',
        howToUse: 'サイドバーの拡張機能アイコンから検索・インストール',
        example: 'Python, ESLint, Prettier, GitLensなどの人気拡張機能が利用可能',
        icon: '🧩'
      },
      {
        name: 'Git統合',
        description: 'Gitの操作をGUIで簡単に実行',
        howToUse: 'サイドバーのソース管理アイコンから変更の確認、コミット、プッシュ',
        example: 'ステージング、コミットメッセージ入力、ブランチ切り替えをUI操作で完結',
        icon: '🔀'
      },
      {
        name: 'リモートデバッグ',
        description: 'ブレークポイントを設定してデバッグ実行',
        howToUse: 'F5キーでデバッグ開始、F9でブレークポイント設定',
        example: 'Node.js、Python、Goなどのデバッグ設定をlaunch.jsonで管理',
        icon: '🐛'
      },
      {
        name: 'IntelliSense',
        description: 'コード補完と型情報の表示',
        howToUse: 'Ctrl+Space で補完候補を表示',
        example: 'TypeScript、JavaScript、Pythonで型に基づいた賢い補完',
        icon: '💡'
      },
      {
        name: 'マルチカーソル編集',
        description: '複数箇所を同時に編集',
        howToUse: 'Alt+Click で複数カーソル配置、Ctrl+D で同じ単語を順次選択',
        example: '変数名の一括リネーム、複数行の同時編集',
        icon: '✏️'
      }
    ],
    useCases: [
      {
        title: 'リモート開発環境',
        scenario: 'どこからでもブラウザ経由で開発作業',
        steps: [
          'Tailscale VPN経由で安全にアクセス',
          'プロジェクトフォルダを開く',
          'コーディング・テスト・デプロイを実行',
          '作業状態を保持したまま場所を移動'
        ],
        benefits: ['環境構築不要', '設定の同期不要', 'リソースをサーバー側で処理']
      },
      {
        title: 'ペアプログラミング',
        scenario: '複数人での共同開発',
        steps: [
          '同じCode Serverインスタンスにアクセス',
          'Live Share拡張機能をインストール',
          'セッションを共有',
          'リアルタイムで共同編集'
        ],
        benefits: ['画面共有不要', 'レスポンシブな操作', '各自のカーソルを追跡']
      },
      {
        title: 'CI/CDパイプライン開発',
        scenario: 'GitHub ActionsやJenkinsfileの編集',
        steps: [
          'YAMLファイルを開く',
          'YAML拡張機能で構文チェック',
          'ターミナルでローカルテスト',
          'Git経由でプッシュ'
        ],
        benefits: ['構文エラーの早期発見', 'テンプレート活用', 'バージョン管理']
      }
    ],
    faq: [
      {
        question: 'デスクトップ版VSCodeとの違いは？',
        answer: '機能はほぼ同じですが、一部のネイティブ拡張機能（C++デバッガーなど）は制限があります。',
        category: '基本'
      },
      {
        question: '拡張機能の同期はできる？',
        answer: 'Settings Syncを使用してGitHub/Microsoftアカウント経由で同期可能です。',
        category: '設定'
      },
      {
        question: 'ファイルサイズの制限は？',
        answer: '50MB以上のファイルは開けない場合があります。大きなファイルはターミナルで処理してください。',
        category: '制限'
      },
      {
        question: 'キーボードショートカットが効かない',
        answer: 'ブラウザのショートカットと競合する場合があります。Settings > Keyboard Shortcutsで変更可能です。',
        category: 'トラブルシューティング'
      }
    ],
    troubleshooting: [
      {
        issue: '接続が遅い・タイムアウトする',
        solution: 'Tailscale VPNが有効か確認。ネットワーク帯域を確認',
        relatedError: 'ERR_CONNECTION_TIMED_OUT',
        preventiveMeasure: 'Keep-alive設定を有効にする'
      },
      {
        issue: '拡張機能がインストールできない',
        solution: 'プロキシ設定を確認。オフライン拡張機能を使用',
        relatedError: 'ENOTFOUND marketplace.visualstudio.com',
        preventiveMeasure: '必要な拡張機能を事前にダウンロード'
      },
      {
        issue: 'ターミナルが文字化けする',
        solution: 'ロケール設定を確認。Terminal > Integrated > Font Familyを変更',
        relatedError: 'Unicode display error',
        preventiveMeasure: 'UTF-8エンコーディングを強制'
      }
    ],
    shortcuts: [
      { keys: 'Ctrl+P', action: 'ファイルを開く', context: '全般' },
      { keys: 'Ctrl+Shift+P', action: 'コマンドパレット', context: '全般' },
      { keys: 'Ctrl+`', action: 'ターミナルを開く', context: 'ターミナル' },
      { keys: 'F5', action: 'デバッグ開始', context: 'デバッグ' },
      { keys: 'Ctrl+Shift+F', action: 'プロジェクト全体検索', context: '検索' },
      { keys: 'Alt+↑/↓', action: '行を移動', context: 'エディタ' },
      { keys: 'Ctrl+/', action: 'コメントトグル', context: 'エディタ' }
    ],
    configuration: {
      files: [
        '~/.config/code-server/config.yaml',
        '~/.local/share/code-server/User/settings.json'
      ],
      environmentVariables: [
        {
          name: 'PASSWORD',
          description: 'Code Serverのアクセスパスワード',
          example: 'export PASSWORD=mysecurepassword'
        }
      ],
      ports: [
        {
          port: 8889,
          protocol: 'HTTP/HTTPS',
          description: 'Code ServerのWebインターフェース'
        }
      ]
    },
    integrations: [
      {
        service: 'Git',
        description: 'バージョン管理システム',
        howTo: 'Git拡張機能がプリインストール済み。認証設定を行うだけ'
      },
      {
        service: 'Docker',
        description: 'コンテナ開発',
        howTo: 'Docker拡張機能をインストールして、リモートコンテナ開発'
      }
    ],
    resources: [
      {
        type: 'doc',
        title: '公式ドキュメント',
        url: 'https://github.com/coder/code-server/blob/main/docs/guide.md',
        language: 'en'
      },
      {
        type: 'github',
        title: 'GitHub リポジトリ',
        url: 'https://github.com/coder/code-server',
        language: 'en'
      }
    ]
  },

  'n8n': {
    id: 'n8n',
    quickStart: {
      title: 'n8nワークフロー作成',
      steps: [
        {
          step: 1,
          title: 'ワークフロー新規作成',
          description: 'Workflow > New でブランクワークフローを作成',
          tip: 'テンプレートから始めることも可能'
        },
        {
          step: 2,
          title: 'ノード追加',
          description: '右側のパネルからノードをドラッグ＆ドロップ',
          tip: '検索機能で目的のノードを素早く見つける'
        },
        {
          step: 3,
          title: 'ノード接続',
          description: 'ノード間を線でつないでフローを作成',
          tip: '複数の出力も可能'
        },
        {
          step: 4,
          title: '実行とテスト',
          description: 'Execute Workflowボタンで実行',
          tip: 'ステップごとのデバッグも可能'
        }
      ]
    },
    features: [
      {
        name: 'ビジュアルワークフロー',
        description: 'ノーコードでワークフロー構築',
        howToUse: 'ドラッグ＆ドロップでノードを配置して接続',
        example: 'メール受信 → データ抽出 → DB保存 → 通知送信',
        icon: '🔄'
      },
      {
        name: '400+統合',
        description: '多数のアプリケーションと連携',
        howToUse: 'ノードライブラリから選択して設定',
        example: 'Slack、Gmail、Notion、GitHub、Airtableなど',
        icon: '🔌'
      },
      {
        name: 'カスタムコード',
        description: 'JavaScriptでカスタムロジック実装',
        howToUse: 'Codeノードで独自の処理を記述',
        example: 'データ変換、API呼び出し、複雑な条件分岐',
        icon: '💻'
      },
      {
        name: 'スケジューリング',
        description: '定期実行やトリガーベースの実行',
        howToUse: 'Cronノードやトリガーノードを設定',
        example: '毎日9時にレポート生成、Webhookで即座に実行',
        icon: '⏰'
      },
      {
        name: 'エラーハンドリング',
        description: 'エラー時の処理フロー',
        howToUse: 'Error Triggerノードでエラー処理',
        example: 'リトライ、通知、代替処理',
        icon: '⚠️'
      }
    ],
    useCases: [
      {
        title: 'データ同期',
        scenario: '異なるシステム間のデータ同期',
        steps: [
          'ソースシステムからデータ取得',
          'データ変換とマッピング',
          'ターゲットシステムへ書き込み',
          '同期ログ記録'
        ],
        benefits: ['リアルタイム同期', 'エラー処理', 'スケーラブル']
      },
      {
        title: 'マーケティング自動化',
        scenario: 'リード管理とメール配信',
        steps: [
          'Webフォームからリード取得',
          'CRMに登録',
          'セグメント分類',
          '自動メール送信'
        ],
        benefits: ['リード育成', '作業効率化', 'パーソナライズ']
      },
      {
        title: 'インシデント対応',
        scenario: 'システム監視とアラート',
        steps: [
          '監視システムからアラート受信',
          '重要度判定',
          '担当者に通知',
          'チケット作成'
        ],
        benefits: ['迅速な対応', '自動エスカレーション', '履歴管理']
      }
    ],
    faq: [
      {
        question: '実行回数に制限はある？',
        answer: 'セルフホスト版は無制限。クラウド版はプランによる制限あり。',
        category: 'ライセンス'
      },
      {
        question: 'ワークフローの共有は可能？',
        answer: 'JSON形式でエクスポート/インポート可能。コミュニティでテンプレート共有も。',
        category: '機能'
      }
    ],
    troubleshooting: [
      {
        issue: 'ワークフローが遅い',
        solution: 'ノード数を減らす、並列処理を活用',
        relatedError: 'Execution timeout',
        preventiveMeasure: '大量データは分割処理'
      },
      {
        issue: '認証エラー',
        solution: '資格情報を再設定、APIキーの有効期限確認',
        relatedError: '401 Unauthorized',
        preventiveMeasure: '定期的な認証情報の更新'
      }
    ],
    shortcuts: [
      { keys: 'Ctrl+S', action: 'ワークフロー保存', context: 'エディタ' },
      { keys: 'Ctrl+Enter', action: 'ワークフロー実行', context: 'エディタ' },
      { keys: 'Tab', action: 'ノード追加パネル', context: 'エディタ' }
    ],
    configuration: {
      ports: [
        {
          port: 5678,
          protocol: 'HTTP',
          description: 'n8n Web UI'
        }
      ]
    },
    resources: [
      {
        type: 'doc',
        title: 'n8n Documentation',
        url: 'https://docs.n8n.io',
        language: 'en'
      },
      {
        type: 'community',
        title: 'n8n Community',
        url: 'https://community.n8n.io',
        language: 'en'
      }
    ]
  },

  'mumuko': {
    id: 'mumuko',
    quickStart: {
      title: 'Mumukoを始める',
      steps: [
        {
          step: 1,
          title: 'アクセス',
          description: 'WebブラウザでMumukoにアクセス',
          tip: '初回は設定ウィザードが表示されます'
        },
        {
          step: 2,
          title: '基本設定',
          description: 'プロフィールと環境設定を行う',
          tip: '使用目的に合わせて最適化'
        },
        {
          step: 3,
          title: '利用開始',
          description: 'ダッシュボードから各機能にアクセス',
          tip: 'ショートカットキーで効率的に操作'
        }
      ]
    },
    features: [
      {
        name: 'ユーザー管理',
        description: 'ユーザーアカウントと権限管理',
        howToUse: '管理画面からユーザー追加・編集',
        example: 'ロールベースアクセス制御（RBAC）',
        icon: '👤'
      },
      {
        name: 'ダッシュボード',
        description: 'カスタマイズ可能な情報表示',
        howToUse: 'ウィジェットを追加・配置',
        example: 'グラフ、統計、通知を一元表示',
        icon: '📊'
      },
      {
        name: 'レポート機能',
        description: '各種レポートの生成と管理',
        howToUse: 'テンプレートから選択またはカスタム作成',
        example: '月次レポート、分析レポート',
        icon: '📈'
      }
    ],
    useCases: [
      {
        title: 'プロジェクト管理',
        scenario: 'チームプロジェクトの進捗管理',
        steps: [
          'プロジェクト作成',
          'タスク割り当て',
          '進捗追跡',
          'レポート生成'
        ],
        benefits: ['可視化', '効率化', 'コラボレーション']
      }
    ],
    faq: [
      {
        question: 'カスタマイズは可能？',
        answer: 'UI、機能、ワークフローなど幅広くカスタマイズ可能です。',
        category: 'カスタマイズ'
      }
    ],
    troubleshooting: [
      {
        issue: 'ログインできない',
        solution: 'パスワードリセットまたは管理者に連絡',
        preventiveMeasure: 'パスワード管理ツールの使用'
      }
    ],
    configuration: {
      ports: [
        {
          port: 8888,
          protocol: 'HTTP',
          description: 'Mumuko Web Interface'
        }
      ]
    },
    resources: [
      {
        type: 'doc',
        title: 'ユーザーガイド',
        url: '/docs/mumuko',
        language: 'ja'
      }
    ]
  },

  'syncthing': {
    id: 'syncthing',
    quickStart: {
      title: 'Syncthingでファイル同期',
      steps: [
        {
          step: 1,
          title: 'デバイス追加',
          description: '同期したいデバイスでSyncthingをインストール',
          tip: 'デバイスIDをメモしておく'
        },
        {
          step: 2,
          title: 'デバイス接続',
          description: 'デバイスIDを使って相互に接続',
          tip: 'QRコードでも簡単接続可能'
        },
        {
          step: 3,
          title: 'フォルダ共有',
          description: '同期したいフォルダを選択して共有',
          tip: '同期タイプ（送信/受信/送受信）を選択'
        }
      ]
    },
    features: [
      {
        name: 'P2P同期',
        description: 'サーバー不要の直接同期',
        howToUse: 'デバイス間で直接通信して同期',
        example: 'クラウドを介さずプライベートに同期',
        icon: '🔄'
      },
      {
        name: '暗号化通信',
        description: 'TLSによる安全な通信',
        howToUse: '自動的に暗号化、追加設定不要',
        example: '転送中のデータは全て暗号化',
        icon: '🔐'
      },
      {
        name: 'バージョン管理',
        description: 'ファイルの変更履歴を保持',
        howToUse: 'Versions設定で履歴数を指定',
        example: '過去30日分のバージョンを保持',
        icon: '📚'
      },
      {
        name: 'ファイル無視',
        description: '.stignoreファイルで同期除外',
        howToUse: '.gitignoreと同様の記法',
        example: '*.tmp, node_modules/, .DS_Store',
        icon: '🚫'
      },
      {
        name: '帯域制限',
        description: 'ネットワーク使用量の制御',
        howToUse: '設定で上り/下り速度を制限',
        example: '業務時間中は1MB/s、夜間は無制限',
        icon: '📶'
      }
    ],
    useCases: [
      {
        title: '開発環境同期',
        scenario: '複数PCでの開発環境共有',
        steps: [
          'プロジェクトフォルダを共有設定',
          '.stignoreでビルド成果物を除外',
          'リアルタイム同期を有効化',
          '各PCで同じ環境で作業'
        ],
        benefits: ['環境の一貫性', 'オフライン対応', '自動バックアップ']
      },
      {
        title: '写真バックアップ',
        scenario: 'スマホ写真の自動バックアップ',
        steps: [
          'スマホにSyncthingアプリインストール',
          'カメラフォルダを共有',
          '送信専用モードに設定',
          'PCで自動受信'
        ],
        benefits: ['自動化', 'プライバシー保護', '容量節約']
      },
      {
        title: 'チームファイル共有',
        scenario: 'チーム内でのドキュメント共有',
        steps: [
          'チームメンバーをデバイス追加',
          '共有フォルダ作成',
          'アクセス権限設定',
          'リアルタイム同期'
        ],
        benefits: ['リアルタイム更新', 'オフライン編集', 'コンフリクト解決']
      }
    ],
    faq: [
      {
        question: 'ファイル競合はどう処理される？',
        answer: '競合ファイルは.sync-conflict-として保存され、手動で解決できます。',
        category: '同期'
      },
      {
        question: '同期速度が遅い',
        answer: '帯域制限設定、ファイアウォール、NAT設定を確認してください。',
        category: 'パフォーマンス'
      }
    ],
    troubleshooting: [
      {
        issue: 'デバイスが接続されない',
        solution: 'ファイアウォールでポート22000/TCPと21027/UDPを開放',
        relatedError: 'Device disconnected',
        preventiveMeasure: 'UPnP有効化またはポート転送設定'
      },
      {
        issue: '同期が始まらない',
        solution: 'フォルダパス、権限、ディスク容量を確認',
        relatedError: 'Folder not syncing',
        preventiveMeasure: '定期的な接続状態確認'
      }
    ],
    configuration: {
      ports: [
        {
          port: 8384,
          protocol: 'HTTP',
          description: 'Web GUI'
        },
        {
          port: 22000,
          protocol: 'TCP',
          description: 'Sync protocol'
        },
        {
          port: 21027,
          protocol: 'UDP',
          description: 'Discovery'
        }
      ]
    },
    resources: [
      {
        type: 'doc',
        title: 'Syncthing Documentation',
        url: 'https://docs.syncthing.net',
        language: 'en'
      },
      {
        type: 'community',
        title: 'Syncthing Forum',
        url: 'https://forum.syncthing.net',
        language: 'en'
      }
    ]
  },

  'file-manager': {
    id: 'file-manager',
    quickStart: {
      title: 'ファイルマネージャー使用開始',
      steps: [
        {
          step: 1,
          title: 'Webインターフェースにアクセス',
          description: 'ブラウザでファイルマネージャーを開く',
          tip: 'ブックマークに追加して素早くアクセス'
        },
        {
          step: 2,
          title: 'ファイル操作',
          description: 'ドラッグ＆ドロップでファイル管理',
          tip: 'Ctrl/Cmdキーで複数選択'
        },
        {
          step: 3,
          title: 'アップロード/ダウンロード',
          description: 'ファイルの転送を実行',
          tip: '大容量ファイルは分割アップロード'
        }
      ]
    },
    features: [
      {
        name: 'ブラウザベース操作',
        description: 'Webブラウザから完全なファイル管理',
        howToUse: '通常のファイルマネージャーと同様の操作',
        example: 'コピー、移動、削除、リネーム、権限変更',
        icon: '📁'
      },
      {
        name: 'マルチユーザー対応',
        description: 'ユーザーごとのアクセス制御',
        howToUse: '管理者がユーザーと権限を設定',
        example: '読み取り専用、編集可能、管理者',
        icon: '👥'
      },
      {
        name: 'ファイルプレビュー',
        description: '画像、動画、ドキュメントのプレビュー',
        howToUse: 'ファイルをクリックして即座にプレビュー',
        example: 'PDF、画像、動画、テキストファイル',
        icon: '👁️'
      },
      {
        name: 'ファイル検索',
        description: '高速なファイル・フォルダ検索',
        howToUse: '検索ボックスに名前やタグを入力',
        example: 'ワイルドカード検索、正規表現対応',
        icon: '🔍'
      },
      {
        name: '共有リンク',
        description: 'ファイル共有用のリンク生成',
        howToUse: '右クリックメニューから共有リンク作成',
        example: '期限付きリンク、パスワード保護',
        icon: '🔗'
      }
    ],
    useCases: [
      {
        title: 'リモートファイルアクセス',
        scenario: '外出先からファイルにアクセス',
        steps: [
          'VPN/Tailscale経由でアクセス',
          'ファイルマネージャーにログイン',
          '必要なファイルを検索',
          'ダウンロードまたは編集'
        ],
        benefits: ['どこからでもアクセス', 'ローカル保存不要', 'セキュア']
      },
      {
        title: 'チームコラボレーション',
        scenario: 'チームでのファイル共有と管理',
        steps: [
          'プロジェクトフォルダ作成',
          'メンバーに権限付与',
          'ファイルアップロード',
          'コメント・タグ付け'
        ],
        benefits: ['権限管理', 'バージョン管理', '監査ログ']
      }
    ],
    faq: [
      {
        question: 'ファイルサイズ制限は？',
        answer: '設定により変更可能。デフォルトは2GB。',
        category: '制限'
      }
    ],
    troubleshooting: [
      {
        issue: 'アップロードが失敗する',
        solution: 'ファイルサイズ制限、ディスク容量、権限を確認',
        relatedError: 'Upload failed',
        preventiveMeasure: '大きなファイルは分割アップロード'
      }
    ],
    shortcuts: [
      { keys: 'Ctrl+A', action: '全選択', context: 'ファイルリスト' },
      { keys: 'F2', action: 'リネーム', context: 'ファイル選択時' },
      { keys: 'Delete', action: '削除', context: 'ファイル選択時' }
    ],
    configuration: {
      ports: [
        {
          port: 8890,
          protocol: 'HTTP',
          description: 'File Manager Web UI'
        }
      ]
    },
    resources: [
      {
        type: 'doc',
        title: 'ユーザーマニュアル',
        url: '/docs/file-manager',
        language: 'ja'
      }
    ]
  },

  'nats': {
    id: 'nats',
    quickStart: {
      title: 'NATSメッセージング開始',
      steps: [
        {
          step: 1,
          title: 'クライアント接続',
          description: 'NATSクライアントライブラリで接続',
          tip: 'nats://localhost:4222がデフォルト',
          command: 'nc, _ := nats.Connect("nats://localhost:4222")'
        },
        {
          step: 2,
          title: 'パブリッシュ',
          description: 'トピックにメッセージを送信',
          command: 'nc.Publish("subject", []byte("message"))'
        },
        {
          step: 3,
          title: 'サブスクライブ',
          description: 'トピックからメッセージ受信',
          command: 'nc.Subscribe("subject", handler)'
        }
      ]
    },
    features: [
      {
        name: 'Pub/Subメッセージング',
        description: 'トピックベースのメッセージ配信',
        howToUse: 'Subject（トピック）を指定して送受信',
        example: 'sensor.temperature.room1に温度データ送信',
        icon: '📨'
      },
      {
        name: 'Request/Reply',
        description: '同期的な要求応答パターン',
        howToUse: 'Request()で送信、自動的に応答を受信',
        example: 'サービス間のRPC実装',
        icon: '↔️'
      },
      {
        name: 'Queue Groups',
        description: 'ロードバランシングとフォールトトレランス',
        howToUse: 'QueueSubscribe()で同じキューグループに参加',
        example: 'ワーカープールでタスク処理',
        icon: '⚖️'
      },
      {
        name: 'JetStream',
        description: '永続化とストリーミング',
        howToUse: 'ストリームとコンシューマーを設定',
        example: 'イベントストア、メッセージ再生',
        icon: '💾'
      },
      {
        name: 'セキュリティ',
        description: 'TLS、認証、認可',
        howToUse: 'TLS証明書とNKey/JWTで認証',
        example: 'mTLS通信、ロールベースアクセス',
        icon: '🔒'
      }
    ],
    useCases: [
      {
        title: 'マイクロサービス通信',
        scenario: 'サービス間の非同期通信',
        steps: [
          'サービスディスカバリー',
          'イベント駆動アーキテクチャ',
          'サービスメッシュ',
          'サーキットブレーカー'
        ],
        benefits: ['疎結合', 'スケーラビリティ', '耐障害性']
      },
      {
        title: 'IoTデータ収集',
        scenario: 'センサーデータの収集と処理',
        steps: [
          'デバイスからデータパブリッシュ',
          'エッジでデータ集約',
          'クラウドへ転送',
          'リアルタイム分析'
        ],
        benefits: ['低遅延', '効率的な帯域使用', 'スケーラブル']
      },
      {
        title: 'リアルタイム通知',
        scenario: 'ユーザーへのプッシュ通知',
        steps: [
          'イベント発生',
          'NATSにパブリッシュ',
          '該当ユーザーに配信',
          '配信確認'
        ],
        benefits: ['即時配信', 'ファンアウト', '信頼性']
      }
    ],
    faq: [
      {
        question: 'NATSとKafkaの違いは？',
        answer: 'NATSは低遅延・シンプル、Kafkaは永続化・大規模ストリーミング向け。',
        category: '比較'
      },
      {
        question: 'メッセージサイズ制限は？',
        answer: 'デフォルト1MB、設定で変更可能（max_payload_size）。',
        category: '制限'
      }
    ],
    troubleshooting: [
      {
        issue: '接続できない',
        solution: 'サーバー起動確認、ポート4222が開いているか確認',
        relatedError: 'Connection refused',
        preventiveMeasure: 'ヘルスチェックエンドポイント監視'
      },
      {
        issue: 'メッセージロス',
        solution: 'JetStreamを使用して永続化、At-Least-Once配信',
        relatedError: 'Message not delivered',
        preventiveMeasure: 'Ackタイムアウト設定'
      }
    ],
    apiEndpoints: [
      {
        method: 'TCP',
        endpoint: 'nats://localhost:4222',
        description: 'NATS通信エンドポイント',
        auth: false
      },
      {
        method: 'HTTP',
        endpoint: 'http://localhost:8222/varz',
        description: '監視API - サーバー状態',
        auth: false
      },
      {
        method: 'WebSocket',
        endpoint: 'ws://localhost:8080',
        description: 'WebSocketゲートウェイ',
        auth: true
      }
    ],
    configuration: {
      ports: [
        {
          port: 4222,
          protocol: 'TCP',
          description: 'Client connections'
        },
        {
          port: 8222,
          protocol: 'HTTP',
          description: 'Monitoring'
        },
        {
          port: 6222,
          protocol: 'TCP',
          description: 'Cluster routing'
        }
      ]
    },
    resources: [
      {
        type: 'doc',
        title: 'NATS Documentation',
        url: 'https://docs.nats.io',
        language: 'en'
      },
      {
        type: 'github',
        title: 'NATS Server',
        url: 'https://github.com/nats-io/nats-server',
        language: 'en'
      }
    ]
  },

  'dashboard': {
    id: 'dashboard',
    quickStart: {
      title: 'ダッシュボード利用開始',
      steps: [
        {
          step: 1,
          title: 'アクセス',
          description: 'ブラウザでダッシュボードにアクセス',
          tip: 'ブックマークしておくと便利'
        },
        {
          step: 2,
          title: 'サービス確認',
          description: '各サービスの稼働状態を確認',
          tip: '緑は正常、赤は異常を示す'
        },
        {
          step: 3,
          title: 'サービスアクセス',
          description: '必要なサービスをクリックしてアクセス',
          tip: '新しいタブで開きます'
        }
      ]
    },
    features: [
      {
        name: 'サービス一覧表示',
        description: '全サービスの状態を一覧表示',
        howToUse: 'ダッシュボードにアクセスすると自動表示',
        example: '各サービスのカード表示とステータス',
        icon: '📋'
      },
      {
        name: 'ヘルスチェック',
        description: '各サービスの稼働状態を自動確認',
        howToUse: '30秒ごとに自動更新',
        example: 'オンライン/オフライン状態の表示',
        icon: '❤️'
      },
      {
        name: 'カテゴリ分類',
        description: 'サービスをカテゴリごとに整理',
        howToUse: '開発、AI、ストレージなどで分類',
        example: 'フィルターで特定カテゴリのみ表示',
        icon: '🏷️'
      },
      {
        name: 'ダークモード',
        description: '目に優しいダークテーマ',
        howToUse: 'システム設定に自動追従',
        example: '夜間は自動的にダークモードに',
        icon: '🌙'
      }
    ],
    useCases: [
      {
        title: 'システム管理',
        scenario: 'システム全体の監視',
        steps: [
          'ダッシュボードにアクセス',
          '全サービスの状態確認',
          '問題があるサービスを特定',
          '該当サービスにアクセスして対処'
        ],
        benefits: ['一元管理', '迅速な問題発見', '効率的な運用']
      }
    ],
    faq: [
      {
        question: '新しいサービスを追加するには？',
        answer: 'services.tsファイルにサービス情報を追加して、再ビルドしてください。',
        category: 'カスタマイズ'
      }
    ],
    troubleshooting: [
      {
        issue: 'サービスカードが表示されない',
        solution: 'ブラウザキャッシュをクリア、再読み込み',
        preventiveMeasure: '定期的なキャッシュクリア'
      }
    ],
    configuration: {
      ports: [
        {
          port: 3000,
          protocol: 'HTTP',
          description: 'Dashboard UI'
        }
      ]
    },
    resources: [
      {
        type: 'github',
        title: 'Dashboard Repository',
        url: 'https://github.com/yourusername/dashboard',
        language: 'en'
      }
    ]
  }
};

export function getServiceDetail(serviceId: string): ServiceDetail | undefined {
  return SERVICE_DETAILS[serviceId];
}