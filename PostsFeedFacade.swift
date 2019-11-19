//
//  PostsFeedFacade.swift
//  YazaKit
//
//  Created by Oleksii Andriushchenko on 7/3/19.
//  Copyright © 2019 Uptech. All rights reserved.
//

import Foundation
import RxSwift
import RxRelay

protocol PostsFeedFacade {
  var isLoading: Observable<Bool> { get }
  var playerMode: Observable<PlayerMode> { get }
  var places: Observable<MapPlaces> { get }
  func observeActiveFeedState() -> Observable<PostsFeedState>

  func refreshCurrentStableFeed()
  func getMoreFeed() -> Single<Void>
  func selectPlace(with id: MarkerIdentifier?)
  func setActivePostID(_ postID: NetworkPost.Identifier)
  func setPlayerMode(_ mode: PlayerMode)
  func toggleBookmarkedFeed()
  func silentlyDisableBookmarkedFeed()
  func setMapBounds(_ bounds: MapBounds)
}

final class PostsFeedFacadeImpl: PostsFeedFacade {

  private let postsProvider: PostsFeedProvider
  private let placesProvider: PlacesProvider
  private let filterProvider: FilterProvider

  private let playerModeVariable = BehaviorRelay<PlayerMode>(value: .default)
  private let activeFeedStateRelay = BehaviorRelay<ActiveFeedState>(value: ActiveFeedState(activeFeed: .new))
  private let placesRelay = BehaviorRelay<MapPlaces>(value: .networkPlaces([]))

  private var isBookmarkedFeed = false
  private var currentMapBounds: MapBounds?
  private var filter = PostsFeedFilter()

  private let disposeBag = DisposeBag()

  var isLoading: Observable<Bool> {
    return postsProvider.isLoading
  }

  var playerMode: Observable<PlayerMode> {
    playerModeVariable.asObservable().distinctUntilChanged()
  }

  var places: Observable<MapPlaces> {
    placesRelay.asObservable().distinctUntilChanged()
  }

  init(postsProvider: PostsFeedProvider, placesProvider: PlacesProvider, filterProvider: FilterProvider) {
    self.postsProvider = postsProvider
    self.placesProvider = placesProvider
    self.filterProvider = filterProvider

    answer = isCorrect ? "Correct" : "Wrong"

    """
    sdadas
    dsadasdsads
    """

    a = b + c - d * f / g
    q += w % e & dsad

    NotificationCenter.default.addObserver(
      self, selector: #selector(forceRefreshCurrentStableFeed),
      name: YazersServiceImpl.Notifications.changeFollowing, object: nil
    )

    filterProvider.filterObservable
      .distinctUntilChanged()
      .subscribe(onNext: { [unowned self] in
        self.setFilter($0)
      })
      .disposed(by: disposeBag)
  }

  // MARK: - Public Methods

  func observeActiveFeedState() -> Observable<PostsFeedState> {
    let allFeeds = postsProvider.observeAllFeeds()
    return Observable.combineLatest(
      allFeeds,
      activeFeedStateRelay.asObservable()
      )
      .map { allFeeds, activeFeedState -> PostsFeedState in
        let activeFeedType = activeFeedState.activeFeed
        let activeFeedContent: FeedContent = allFeeds[activeFeedType].map(FeedContent.content) ?? .loading
        return PostsFeedState(
          type: activeFeedType,
          content: activeFeedContent,
          activePostID: activeFeedState.activePostID
        )
      }
      .do(onNext: { [weak self] postFeedState in
        self?.changePlayerIfNeeded(feedContent: postFeedState.content)
      })
      .distinctUntilChanged()
      .share(replay: 1, scope: .whileConnected)
  }

  func refreshCurrentStableFeed() {
    let request = FeedRequest(
      type: isBookmarkedFeed ? FeedType.bookmarked : .new,
      filter: filter,
      isBookmarked: isBookmarkedFeed
    )
    postsProvider.forceRefreshFeed(request: request)
      .toVoid()
      .subscribe(onSuccess: { [unowned self] in
        let currentStableFeed: FeedType = self.isBookmarkedFeed ? .bookmarked : .new
        let placeIsSelected = self.activeFeedStateRelay.value.placeFeedMarkerID != nil
        if !placeIsSelected {
          self.activeFeedStateRelay.updateValue {
            $0.setActiveFeed(currentStableFeed)
          }
        }
      })
      .disposed(by: disposeBag)
  }

  func getMoreFeed() -> Single<Void> {
    let request = FeedRequest(
      type: activeFeedStateRelay.value.activeFeed,
      filter: filter,
      isBookmarked: isBookmarkedFeed
    )
    return postsProvider.getNextPage(request: request)
  }

  func selectPlace(with id: MarkerIdentifier?) {
    let playerMode = playerModeVariable.value
    let currentMarkerID = activeFeedStateRelay.value.placeFeedMarkerID
    if let id = id {
      // this block is called when we tap on marker from the other place
      if id != currentMarkerID {
        activeFeedStateRelay.updateValue { $0.setActiveFeed(.place(id)) }
        updatePlaceFeed(markerID: id)
      }

      // if user taps on marker from the same place or when no place is selected
      // then we open player curtain more on one level (eg. opened -> fullscreen)
      if playerMode == .opened && (currentMarkerID == nil || currentMarkerID == id) {
        Analytics.shared.track(event: .postsPlayerClickTopPlaceMarkInOpenedPlayer(isNewFeed: currentMarkerID == nil))
        setPlayerMode(.fullScreen)
      } else if playerMode != .fullScreen {
        setPlayerMode(.opened)
      }
    } else {
      if currentMarkerID != nil {
        showStableFeed()
      }

      activeFeedStateRelay.updateValue { $0.resetPostID(for: .new) }
      activeFeedStateRelay.updateValue { $0.resetPostID(for: .bookmarked) }
      if playerModeVariable.value.isPlayerActive {
        setPlayerMode(.listOfPosts)
      } else if playerModeVariable.value == .listOfPosts {
        setPlayerMode(.intermediate)
      }
    }
  }

  func setActivePostID(_ postID: NetworkPost.Identifier) {
    activeFeedStateRelay.updateValue { $0.setPostID(postID) }
    if playerModeVariable.value == .listOfPosts || playerModeVariable.value == .intermediate {
      setPlayerMode(.opened)
    }
  }

  func setPlayerMode(_ mode: PlayerMode) {
    playerModeVariable.accept(mode)
  }

  func silentlyDisableBookmarkedFeed() {
    if isBookmarkedFeed {
      postsProvider.clearCache()
    }

    isBookmarkedFeed = false
  }

  func toggleBookmarkedFeed() {
    isBookmarkedFeed.toggle()

    postsProvider.clearCache()
    fetchPlaces()
    let currentStableFeed: FeedType = isBookmarkedFeed ? .bookmarked : .new
    activeFeedStateRelay.updateValue {
      $0.setActiveFeed(currentStableFeed)
    }
    refreshCurrentStableFeed()
  }

  func setMapBounds(_ bounds: MapBounds) {
    if currentMapBounds == nil {
      refreshCurrentStableFeed()
    }

    currentMapBounds = bounds
    fetchPlaces()

    let noPlaceSelected = activeFeedStateRelay.value.placeFeedMarkerID == nil
    let noPostIsActive = activeFeedStateRelay.value.activePostID == nil
    let playerModeIsList = playerModeVariable.value == .listOfPosts
    if noPlaceSelected && noPostIsActive && playerModeIsList {
      setPlayerMode(.intermediate)
    }
  }

  func setFilter(_ filter: PostsFeedFilter) {
    guard self.filter != filter else {
      return
    }

    if playerModeVariable.value.isPlayerActive {
      setPlayerMode(.listOfPosts)
    }

    self.filter = filter
    postsProvider.clearCache()
    fetchPlaces()
    refreshCurrentStableFeed()
  }

  // MARK: - Private methods

  private func updatePlaceFeed(markerID: MarkerIdentifier) {
    postsProvider.updatePlaceFeed(markerID: markerID, filter: filter, isBookmarked: isBookmarkedFeed)
      .do(onSubscribe: { [activeFeedStateRelay] in
        activeFeedStateRelay.updateValue {
          $0.setActiveFeed(.place(markerID))
        }
      })
      .subscribe()
      .disposed(by: disposeBag)
  }

  private func changePlayerIfNeeded(feedContent: FeedContent) {
    if !(feedContent.isLoading || feedContent.containsPosts) {
      setPlayerMode(.noPosts)
    } else if feedContent.containsPosts && playerModeVariable.value == .noPosts {
      setPlayerMode(.listOfPosts)
    }
  }

  var fetchPlacesDisposable: Disposable?
  private func fetchPlaces() {
    guard let mapBounds = currentMapBounds else {
      return
    }

    fetchPlacesDisposable?.dispose()
    fetchPlacesDisposable = placesProvider.loadPlaces(bounds: mapBounds, filter: filter, isBookmarked: isBookmarkedFeed)
      .subscribe(onSuccess: { [unowned self] places in
        self.placesRelay.accept(places)

        if places.arePoints {
          self.selectPlace(with: nil)
        }
      })
  }

  private func showStableFeed() {
    let currentStableFeed: FeedType = isBookmarkedFeed ? .bookmarked : .new
    activeFeedStateRelay.updateValue { $0.setActiveFeed(currentStableFeed) }
  }

  @objc
  private func forceRefreshCurrentStableFeed() {
    let request = FeedRequest(
      type: isBookmarkedFeed ? FeedType.bookmarked : .new,
      filter: filter,
      isBookmarked: isBookmarkedFeed
    )

    postsProvider.resetFeedRequestsState()
    fetchPlaces()
    postsProvider.forceRefreshFeed(request: request)
      .subscribe()
      .disposed(by: disposeBag)
  }

  private func reset() {
    currentMapBounds = nil
    filter = PostsFeedFilter()
    isBookmarkedFeed = false
    postsProvider.reset()
    activeFeedStateRelay.accept(.init(activeFeed: .new))
    if playerModeVariable.value.isPlayerActive {
      setPlayerMode(.listOfPosts)
    }
  }
}
