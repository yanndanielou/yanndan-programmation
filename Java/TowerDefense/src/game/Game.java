package game;

import java.util.ArrayList;
import java.util.List;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import belligerents.Attacker;
import belligerents.Tower;
import belligerents.listeners.AttackerListener;
import belligerents.listeners.TowerListener;
import builders.GameObjectsDataModel;
import game_board.GameBoard;
import time.TimeManager;

public class Game implements TowerListener, AttackerListener {
	private static final Logger LOGGER = LogManager.getLogger(Game.class);

	private ArrayList<GameListener> game_listeners = new ArrayList<>();
	private ArrayList<GameStatusListener> game_status_listeners = new ArrayList<>();

	private ArrayList<Tower> towers = new ArrayList<>();
	private ArrayList<Attacker> attackers = new ArrayList<>();

	private GameBoard gameBoard;

	private boolean lost = false;
	private boolean over = false;
	private boolean won = false;

	private boolean begun = false;

	private GameObjectsDataModel gameObjectsDataModel;

	public Game(GameBoard gameBoard, GameObjectsDataModel game_objects_data_model) {
		this.gameBoard = gameBoard;
		this.gameObjectsDataModel = game_objects_data_model;
		gameBoard.setGame(this);
		add_game_status_listener(TimeManager.getInstance());

	}

	public void add_game_listener(GameListener listener) {
		listener.onListenToGame(this);
		game_listeners.add(listener);
	}

	public void add_game_status_listener(GameStatusListener listener) {
		listener.onListenToGameStatus(this);
		game_status_listeners.add(listener);
	}

	public void cancel() {
		game_status_listeners.forEach((game_status_listener) -> game_status_listener.onGameCancelled(this));
	}

	public void setLost() {
		LOGGER.info("Game is lost!");
		lost = true;
		over = true;
		game_status_listeners.forEach((game_status_listener) -> game_status_listener.onGameLost(this));
	}

	public void setWon() {
		LOGGER.info("Game is won!");
		won = true;
		over = true;
		game_status_listeners.forEach((game_status_listener) -> game_status_listener.onGameWon(this));
	}

	public boolean isLost() {
		return lost;
	}

	public boolean isOver() {
		return over;
	}

	public boolean isWon() {
		return won;
	}

	public boolean isBegun() {
		return begun;
	}

	public void start() {
		this.begun = true;
		LOGGER.info("Game has started. " + this);
		game_status_listeners.forEach((game_status_listener) -> game_status_listener.onGameStarted(this));
	}

	public GameBoard getGameBoard() {
		return gameBoard;
	}

	public GameObjectsDataModel getGameObjectsDataModel() {
		return gameObjectsDataModel;
	}

	@Override
	public void on_listen_to_tower(Tower tower) {
		towers.add(tower);
	}

	@Override
	public void onAttackerEndOfDestructionAndClean(Attacker attacker) {
		// TODO Auto-generated method stub

	}

	@Override
	public void onListenToAttacker(Attacker attacker) {
		attackers.add(attacker);
	}

	@Override
	public void on_attacker_moved(Attacker attacker) {
		// TODO Auto-generated method stub

	}

	@Override
	public void onAttackerBeginningOfDestruction(Attacker attacker) {
		attackers.remove(attacker);
	}

	@Override
	public void on_tower_removal(Tower tower) {
		towers.remove(tower);
	}

	public List<Attacker> getAttackers() {
		return attackers;
	}

}